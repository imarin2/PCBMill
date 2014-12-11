import subprocess
from SimpleCV import Image
import time

import sys, os
import serial
from subprocess import call
import numpy as np

import cv2
import cv

#Args
try:
        logfile=str(sys.argv[1]) #param for the log file
        log_trace=str(sys.argv[2])      #trace log file
except:
        print "Missing Log reference"

print "json: "+logfile
print "trace: "+log_trace

cycle=True
s_warning=s_error=s_skipped=0


def trace(string):
        global log_trace
        out_file = open(log_trace,"a+")
        out_file.write(str(string) + "\n")
        out_file.close()
        #headless
        print string
        return
        
def printlog():
        global logfile
        #write log
        handle=open(logfile,'w+')
        return  


def read_serial(gcode):
        serial.flushInput()
        serial.write(gcode + "\r\n")
        time.sleep(0.1)
        
        #return serial.readline().rstrip()
        response=serial.readline().rstrip()
        
        if response=="":
                return "NONE"
        else:
                return response

def macro(code,expected_reply,timeout,error_msg,delay_after,warning=False,verbose=True):
        global s_error
        global s_warning
        global s_skipped
        serial.flushInput()
        if s_error==0:
                serial_reply=""
                macro_start_time = time.time()
                serial.write(code+"\r\n")
                if verbose:
                        trace(error_msg)
                time.sleep(0.3) #give it some tome to start
                while not (serial_reply==expected_reply or serial_reply[:4]==expected_reply):
                        #Expected reply
                        #no reply:
                        if (time.time()>=macro_start_time+timeout+5):
                                if serial_reply=="":
                                        serial_reply="<nothing>"
                                if not warning:
                                        s_error+=1
                                        trace(error_msg + ": Failed (" +serial_reply +")")
                                else:
                                        s_warning+=1
                                        trace(error_msg + ": Warning! ")
                                return False #leave the function
                        serial_reply=serial.readline().rstrip()
                        #add safety timeout
                        time.sleep(0.2) #no hammering
                        pass
                time.sleep(delay_after) #wait the desired amount
        else:
                trace(error_msg + ": Skipped")
                s_skipped+=1
                return False
        return serial_reply

#stitch_images will stitch a left/right image by default
#pass vertical and horizontal parameters as needed to stitch images
def stitch_images(image1, image2, vertical=False, horizontal=True, transparency = 1.0, useMask = False):
  #vertical/horizontal dimension multiplier
  v = 1
  h = 1
  if vertical:
    v = 2
  if horizontal:
    h = 2

  #create destination image
  #ASSUMPTION: img1 and img2 have the same dimensions

  dst = Image((image1.width*h, image1.height*v))

  # Find the keypoints.
  match_features = image1.findKeypointMatch(image2)
  match_features[0].draw(width=5)

  #create and use mask to properly blit the (typically last) image
  blitMask = Image(dst.size())
  if useMask:
    #may need overlap here to get better stitching results
    topLeftX = match_features[0].getMinRect()[0][0]+250
    topLeftY = match_features[0].getMinRect()[0][1]+250
    width = match_features[0].getMinRect()[3][0]-match_features[0].getMinRect()[0][0]
    height = match_features[0].getMinRect()[1][1] - match_features[0].getMinRect()[0][1]

    #create a mask to ensure blit in the proper area
    dl = DrawingLayer(dst.size())
    dl.rectangle((topLeftX, topLeftY), (width, height), filled = True, color=Color.WHITE)
    blitMask.addDrawingLayer(dl)
    blitMask = blitMask.applyLayers()
    blitMask = blitMask.invert()
    blitMask.save("mask.jpg")
    # dl.circle((300,300), 80, filled = True, color = Color.WHITE)
  # The homography matrix.
  homo = match_features[0].getHomography()
  #Uncomment if want to prevent perspective shift
  # homo[2][0] = 0
  # homo[2][1] = 0
  # homo[2][2] = 1

  #only 2D translation and rotation.. I think
  affine_transform = np.array([homo[0], homo[1]])

  dst_mat = dst.getMatrix()

  # transform the image.
  # should crop out the overlapping parts to avoid weird darkening etc.
  # Image constructor: Image(source=None, camera=None, colorSpace=0, verbose=True, sample=False, cv2image=False, webp=False)
  # cv2.warpPerspective(src, M, dsize[, dst[, flags[, borderMode[, borderValue]]]])

  #warpPerspective Implementation
  stitched_image = Image(
            #consider using warpAffine here since we can assume no 3D perspective change
            cv2.warpPerspective(
                                np.array((image2.getMatrix()))
                                , homo
                                , (dst_mat.rows, dst_mat.cols)
                                , np.array(dst_mat)
                                , cv2.INTER_CUBIC
                                )
            , colorSpace=ColorSpace.RGB
            )#.toBGR()

  # AFFINE ONLY IMPLEMENTATION
  # Doesn't seem to work too well..
  # x = Image(
  #           #consider using warpAffine here since we can assume no 3D perspective change
  #           cv2.warpAffine(
  #                               np.array((img2.getMatrix()))
  #                               , affine_transform
  #                               , (dst_mat.rows, dst_mat.cols+300)
  #                               , np.array(dst_mat)
  #                               , cv2.INTER_CUBIC
  #                               )
  #           , colorSpace=ColorSpace.RGB
  #           ).toBGR()

  if useMask:
    stitched_image = stitched_image.blit(image1, mask=blitMask)
  else:
    stitched_image = stitched_image.blit(image1)

  return stitched_image

#getKeypointMatch finds the keypointmatches and returns an affine transformation matrix
def getKeypointMatch(src,template,quality=500.00,minDist=0.2,minMatch=0.4):

        try:
            import cv2
        except:
            warnings.warn("Can't Match Keypoints without OpenCV >= 2.3.0")
            return
        if template == None:
          return None


        fs = FeatureSet()
        skp,sd = src._getRawKeypoints(quality)
        tkp,td = template._getRawKeypoints(quality)
        if( skp == None or tkp == None ):
            warnings.warn("I didn't get any keypoints. Image might be too uniform or blurry." )
            return None

        template_points = float(td.shape[0])
        sample_points = float(sd.shape[0])
        magic_ratio = 1.00
        if( sample_points > template_points ):
            magic_ratio = float(sd.shape[0])/float(td.shape[0])

        idx,dist = src._getFLANNMatches(sd,td) # match our keypoint descriptors
        p = dist[:,0]
        result = p*magic_ratio < minDist #, = np.where( p*magic_ratio < minDist )
        pr = result.shape[0]/float(dist.shape[0])

        if( pr > minMatch and len(result)>4 ): # if more than minMatch % matches we go ahead and get the data
            lhs = []
            rhs = []
            for i in range(0,len(idx)):
                if( result[i] ):
                    lhs.append((tkp[i].pt[1], tkp[i].pt[0]))
                    rhs.append((skp[idx[i]].pt[0], skp[idx[i]].pt[1]))

            rhs_pt = np.array(rhs)
            lhs_pt = np.array(lhs)

            if( len(rhs_pt) < 16 or len(lhs_pt) < 16 ):
                return None

            #TO-DO: figure out correct format for lhs_pt and rhs_pt
            affineTransform = cv2.estimateRigidTransform(lhs_pt, rhs_pt, False)

            return affineTransform

            # homography = []
            # (homography,mask) = cv2.findHomography(lhs_pt,rhs_pt,cv2.RANSAC, ransacReprojThreshold=1.0 )
            # w = template.width
            # h = template.height
            #
            # pts = np.array([[0,0],[0,h],[w,h],[w,0]], dtype="float32")
            #
            # pPts = cv2.perspectiveTransform(np.array([pts]), homography)
            #
            # pt0i = (pPts[0][0][1], pPts[0][0][0])
            # pt1i = (pPts[0][1][1], pPts[0][1][0])
            # pt2i = (pPts[0][2][1], pPts[0][2][0])
            # pt3i = (pPts[0][3][1], pPts[0][3][0])
            #
            # #construct the feature set and return it.
            # fs = FeatureSet()
            # fs.append(KeypointMatch(self,template,(pt0i,pt1i,pt2i,pt3i),homography))
            # #the homography matrix is necessary for many purposes like image stitching.
            # #fs.append(homography) # No need to add homography as it is already being
            # #added in KeyPointMatch class.
            # #return fs
        else:
            return None

trace("PCB Clad Detection Initiated")
port = '/dev/ttyAMA0'
baud = 115200

#initialize serial
serial = serial.Serial(port, baud, timeout=0.6)
serial.flushInput()

macro("M741","TRIGGERED",2,"Front panel door control",1, verbose=False) 
macro("M402","ok",2,"Retracting Probe (safety)",1, warning=True, verbose=False) 
macro("G27","ok",100,"Homing Z - Fast",0.1)     

macro("G90","ok",5,"Setting abs mode",0.1, verbose=False)
macro("G92 Z241.2","ok",5,"Setting correct Z",0.1, verbose=False)
#M402 #DOUBLE SAFETY!
macro("M402","ok",2,"Retracting Probe (safety)",1, verbose=False)

macro("G0 X0 Y0 Z200 F5000","ok",5,"Moving to start Z height",10)

init_pos = 0
end_pos = 200
spacing = 20

n_pos = int((end_pos-init_pos)/spacing)

panorama_shot_positions=np.linspace(init_pos, end_pos, n_pos)

trace("Taking camera shots...")

for (p,ypos) in enumerate(panorama_shot_positions):
	macro("G0 X10 Y"+str(ypos)+" F10000","ok",15,"Moving to Position: "+str(p),0.1, warning=True,verbose=True)
	subprocess.call("sudo raspistill -hf -vf --exposure off -awb sun -ISO 400 -w 1920 -h 1080 -o /var/www/temp/pan_%s.jpg -t 0" % p, shell=True)

img = Image("/var/www/temp/pan_0.jpg")

trace("Stiching the camera shots...")

photos=enumerate(panorama_shot_positions)

next(photos)
for (p,ypos) in photos:
	trace("Stiching image %s" % p )
	imgtmp = Image("/var/www/temp/pan_%s.jpg" % p )
	img = stitch_images(img, imgtmp, True, False)

img.save("/var/www/temp/photo.jpg")

#img1 = Image("s.jpg")
#img2 = Image("t.jpg")
#dst = Image((2000, 1600))
#fs = img1.findKeypointMatch(img2)
#homo = fs[0].getHomography()
#eh = dst.getMatrix()
#x = Image(cv2.warpPerspective(np.array((img2.getMatrix())), homo, (eh.rows, eh.cols+300), np.array(eh), cv2.INTER_CUBIC), colorSpace=ColorSpace.RGB).toBGR()


#img = Image("/var/www/temp/pan_2.jpg")

#img.show()
#time.sleep(5)
