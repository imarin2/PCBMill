import time
import sys, os
import serial
from subprocess import call
import numpy as np
import json
import pprint
import CNC


global retractProbe
global feedrate
global num_probes
global start_time

num_probes = 1
retractProbe = False
feedrate = 200
start_time = time.time()

#Args
try:
	global probed_points
	global bed_measured_points
	log_file=str(sys.argv[1]) #param for the log file
	log_trace=str(sys.argv[2])	#trace log file
	points_file = str(sys.argv[3])  # points file
	
	initialProbeHeight = float(sys.argv[4])
	if (initialProbeHeight<50):
		initialProbeHeight = 50; #For Safety
	
	gcode_file = str(sys.argv[5]);

	dozero = str(sys.argv[6]); # 0 = do not Zero, 1 = do Zero

	zoffset_ovr = float(sys.argv[7]);
	pointsFile = open(points_file, "r") 
	bedPoints=pointsFile.read()
	bed_measurement_points = json.loads(bedPoints) #np.array(json.loads(bedPoints))
	probed_points=bed_measurement_points[:-1] #all but last, because the dimensions are in the last
	
except:
	print "Missing Log reference"
	trace("Missing Parameters!")
	sys.exit()


#num of probes each point

s_warning=s_error=s_skipped=0

#first screw offset (lower left corner)
screw_offset=[8.726,10.579,0]

serial_reply=""

def trace(string):
	global log_trace
	out_file = open(log_trace,"a+")
	out_file.write(str(string) + "\n")
	out_file.close()
	#headless
	print string
	return

def response(string):
    
    global log_file
    #print log_file
    out_file_trace = open(log_file,"a+")
    out_file_trace.write(str(string) + "\n")
    out_file_trace.close()
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

trace("Zeroing and Autoleveling")
port = '/dev/ttyAMA0'
baud = 115200

#initialize serial
serial = serial.Serial(port, baud, timeout=0.6)
serial.flushInput()

macro("M18","ok",2,"Motors off",0.5, warning=True, verbose=False)

macro("M402","ok",2,"Retracting Probe (safety)",1, verbose=False)	
macro("G90","ok",2,"Abs_mode",1, verbose=False)

z_safety= 5; # 5 mm of clearance with PCB

trace("Zeroing this tool\r\n")
zeropoint=probed_points[0];
zp=zeropoint[2]+z_safety

macro("G90","ok",2,"Abs_mode",1, verbose=False)
macro("M746 S1","ok",2,"Enabling external probe",1, verbose=False)

if dozero == 1:
	x=zeropoint[0]
	y=zeropoint[1]
	# Go to zero position
	macro("G0 X"+str(x)+" Y"+str(y)+" Z"+str(zp)+" F10000","ok",15,"Moving to Pos",0, warning=True,verbose=False)
	macro("G92 X0 Y0","ok",2,"Setting Local coordinate system",1, verbose=True)
	
# probe with the new tool to set zero
serial.flushInput()
serial.write("G38 S100\r\n")
probe_start_time = time.time()

data=""

while not data[:22]=="echo:endstops hit:  Z:":
   data=serial.readline().rstrip() 
   if (time.time() - probe_start_time>240):  #timeout management
   	trace("Touch probing failed")
        response("false")
        response("false")
	sys.exit("Can not touch the PCB")
        break   
   pass

# we do not actually care of the z touching value of this tool, we just want to set the zero.
macro("G92 X0 Y0 Z"+str(-zoffset_ovr),"ok",2,"Set Zero",1, verbose=False)
#macro("G91","ok",2,"Relative_mode",1, verbose=False)
#macro("G0 Z"+str(zoffset_ovr)+" F10000","ok",15,"Moving to Pos",0, warning=True,verbose=False)
macro("G90","ok",2,"Abs_mode",1, verbose=False)

macro("M746 S0","ok",2,"Disabling external probe",1, verbose=False)

#zoffset_ovr

trace("Leveling gcode file...\r\n")
gcode = CNC.GCode();

gcode.load(gcode_file)

output_file='/var/www/fabui/application/plugins/pcbmill/python/temp/'+os.path.basename(gcode_file)
#print output_file
#points_file='probe.pts';
#pointsFile = open(points_file, "r") 
#bedPoints=pointsFile.read()
#bed_measurement_points = json.loads(bedPoints) #np.array(json.loads(bedPoints))
#probed_points=bed_measurement_points[:-1] #all but last, because the dimensions are in the last

#calculate xmin, xmax, xn, ymin, ymax, yn, zmin, zmax
xn=bed_measurement_points[-1][0]+1;
yn=bed_measurement_points[-1][1]+1;
xmin=0
ymin=0
zmin=0
xmax=0
ymax=0
zmax=0
feed=200

xzero=bed_measurement_points[0][0];
yzero=bed_measurement_points[0][1];
zzero=bed_measurement_points[0][2];

for (p,point) in enumerate(probed_points):
        xt = point[0]-xzero;
        yt = point[1]-yzero;
        zt = point[2]-zzero;

        if xt < xmin:
                xmin = xt;
        if yt < ymin:
                ymin = yt;
        if zt < zmin:
                zmin = zt;
        if xt > xmax:
                xmax = xt;
        if yt > ymax:
                ymax = yt;
        if zt > zmax:
                zmax = zt;

gcode.probe.xmin=xmin;
gcode.probe.ymin=ymin;
gcode.probe.zmin=zmin;
gcode.probe.xmax=xmax;
gcode.probe.ymax=ymax;
gcode.probe.zmax=zmax;
gcode.probe.xn=xn;
gcode.probe.yn=yn;
gcode.probe.feed=feed;

gcode.probe.makeMatrix();
gcode.probe.xstep();
gcode.probe.ystep();


# now the header is known; insert values
for (p,point) in enumerate(probed_points):
        gcode.probe.add(point[0]-xzero,point[1]-yzero,point[2]-zzero);

#gcode.probe.setZero(0,0)

#gcode.probe.save("bCNC_probe.txt")
# Here the probe should be initialized

#gcode.save("gcode_as_Read.gcode")


lines,paths = gcode.prepare2Run(); # this autolevels the code

out_file = open(output_file,"w")

for line in lines:
        if line is not None:
                out_file.write(str(line) + "\n")
                #self.queue.put(line+"\n")

out_file.close()

if (os.path.isfile(output_file)):
	response(output_file)
	response("true")
else:
	response("false")
	response("false")

trace("Done!")
sys.exit()
