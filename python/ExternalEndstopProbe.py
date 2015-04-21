#bed leveling tool
import time
import sys, os
import serial
from subprocess import call
import numpy as np
import json
import pprint

global retractProbe
global feedrate
global num_probes
global start_time

global bedScanXGranularityNr
global bedScanYGranularityNr


num_probes = 1
retractProbe = False
feedrate = 200
start_time = time.time()

#Args
try:
	global probed_points
	logfile=str(sys.argv[1]) #param for the log file
	log_trace=str(sys.argv[2])	#trace log file
	points_file = str(sys.argv[3])  # points file

	initialProbeHeight = float(sys.argv[4])
	if (initialProbeHeight<50):
		initialProbeHeight = 50; #For Safety
	
	calibrationMethod = str(sys.argv[5]).upper()

	accuracy = int(sys.argv[6])

	if (accuracy == 0):
		feedrate = 200	
		retractProbe = False
		num_probes = 1
	if (accuracy == 50): 
		feedrate = 100
		retractProbe = True
		num_probes = 2
	if (accuracy == 100):
		feedrate = 50
		retractProbe = True
		num_probes = 4
	if (accuracy == 150):
		feedrate = 20
		retractProbe = True
		num_probes = 8
	if (accuracy == 200):
		feedrate = 20
		retractProbe = True
		num_probes = 16 
	
	if (calibrationMethod == "BED_MEASUREMENT" or calibrationMethod == "SCREW_CALIBRATION"):
		pointsFile = open(points_file, "r") 
		bedPoints=pointsFile.read()
		bed_measurement_points = json.loads(bedPoints) #np.array(json.loads(bedPoints))
		probed_points=bed_measurement_points[:-1] #all but last, because the dimensions are in the last
		bedScanXGranularityNr=bed_measurement_points[-1][0];
		bedScanYGranularityNr=bed_measurement_points[-1][1];

	
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
	
def printlog():
	global logfile
	global nrPointsToMeasure 
	global pointsMeasured
	str_log='{"bed_calibration":{ '
	str_log+= '"point_measurements":'
	
	pts = '['
	for idx in range(0, len(probed_points)):
		pts = pts + '['
		for idxPt in range(0, len(probed_points[idx])-1):
			if (type(probed_points[idx][idxPt]) in (tuple, list)):
				pts = pts + '['
				for idxPt2 in range(0, len(probed_points[idx][idxPt])-1):
					pts = pts + '"' + (str(probed_points[idx][idxPt][idxPt2])).replace("'", '') + '",'
				pts = pts + '"'+ (str(probed_points[idx][idxPt][len(probed_points[idx][idxPt])-1])).replace("'", '')+'"'
				pts = pts + ']'
 				if  (idxPt<len(probed_points[idx])-1):
					pts = pts +', '
			else:
				pts = pts + '"'+(str(probed_points[idx][idxPt])).replace("'", '') +'", '
		pts = pts + '"' +(str(probed_points[idx][len(probed_points[idx])-1])).replace("'", '') + '"]'
		if  (idx<len(probed_points)-1):
			pts = pts +', '
	pts = pts + ']'
	str_log += pts
	#str_log+= json.dumps(probed_points.tolist()) 
	str_log += '}, "progress" : { '
	str_log += '"pointsMeasured": '+str(pointsMeasured)+', '
	str_log += '"pointsToMeasure": '+str(nrPointsToMeasure)
	str_log += '},'
	str_log += '"measurementInformation": { ' 
	str_log += '"feedrate" : '+str(feedrate)+', '
	str_log += '"probesPerPoint" :'+str(num_probes)+', ' 
	str_log += '"bedScanXGranularityNr" :'+str(bedScanXGranularityNr)+', ' 
	str_log += '"bedScanYGranularityNr" :'+str(bedScanYGranularityNr)+', ' 

	current_time = time.time()
	delta_time = current_time - start_time
	if (pointsMeasured!=0):
		eta_time = (nrPointsToMeasure-pointsMeasured) *  (delta_time / pointsMeasured)
	else:
		eta_time = 60  # time is unknown assume 1 minute 

	hours, rest = divmod(delta_time,3600)
	minutes, seconds = divmod(rest, 60)	

	# Format Time in better readable Format
	hoursStr = str(int(hours))
	minutesStr = str(int(minutes))
	secondsStr = str(int(seconds))
	if (len(hoursStr)<2):
		hoursStr = "0"+hoursStr
	if (len(minutesStr)<2):
		minutesStr = "0"+minutesStr
	if (len(secondsStr)<2):
		secondsStr = "0"+secondsStr	

	str_log += '"time_left" : "'+hoursStr+':'+minutesStr+':'+secondsStr + '"'

	str_log += '}}'

	#write log
	handle=open(logfile,'w+')
	print>>handle, str_log
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

trace("External Endstop Probing")
port = '/dev/ttyAMA0'
baud = 115200

#initialize serial
serial = serial.Serial(port, baud, timeout=0.6)
serial.flushInput()

macro("M402","ok",2,"Retracting Probe (safety)",1, verbose=False)
macro("M746 S1","ok",2,"Enabling external probe",1, verbose=False)	

nrPointsToMeasure = 0
pointsMeasured = 0
for i in range(0,len(probed_points)):
	if (probed_points[i][3]==True):
		nrPointsToMeasure+=1 

nrPointsToMeasure*=num_probes

z_safety= 5; # 5 mm of clearance with PCB
z_toolchange= 30; # 30 mm from PCB to allow for a rapid still confortable change

for (p,point) in enumerate(probed_points):
	zp=point[2]+z_safety

	if (point[3]==True):
		#real carriage position
		x=point[0]
		y=point[1]
		macro("G0 X"+str(x)+" Y"+str(y)+" Z"+str(zp)+" F10000","ok",15,"Moving to Pos",0, warning=True,verbose=False)		
		#Touches 4 times the bed in the same position
		probes=num_probes #temp
		point[2] = ["" for x in range(num_probes)] #np.empty(num_probes)
		for i in range(0,num_probes):
			# Raise probe first, to level out errors of probe retracts?!?
#			if (retractProbe == True):
#				macro("M402","ok",2,"Raising Probe",1, warning=True, verbose=False)	

			#M401
#			macro("M401","ok",2,"Lowering Probe",1, warning=True, verbose=False)	
		
			serial.flushInput()
			#G38	
			serial.write("G38 S100\r\n")
			#time.sleep(0.5)			#give it some to to start	
			probe_start_time = time.time()
			while not serial_reply[:22]=="echo:endstops hit:  Z:":
				serial_reply=serial.readline().rstrip()	
				#issue G38 and waits reply.
				if (time.time() - probe_start_time>240):	#timeout management
					trace("Probe failed on this point")
					probes-=1 #failed, update counter
					point[2][i]("N/A")
					break	
				pass
			
			#print serial_reply
			#get the z position
			if serial_reply!="":
				z=serial_reply.split("Z:")[1].strip()
				#trace("probe no. "+str(i+1)+" = "+str(z) )
				point[2][i]=z # store Z
			
			serial_reply=""
			serial.flushInput()
			pointsMeasured+=1
			msg="Measuring point " +str(pointsMeasured)+ "/"+ str(nrPointsToMeasure) + " (" +str(num_probes) + " times)"
			trace(msg)
			printlog()
		
			#G0 Z40 F5000
			if(num_probes>1):
				macro("G0 Z"+str(zp)+" F5000","ok",10,"Rising Bed",0, warning=True, verbose=False)
		
		#mean of the num of measurements
	

	macro("G0 Z"+str(zp)+" F5000","ok",2,"Rising Bed",0.5, warning=True, verbose=False)
	
#now we have all the points, we move to the tool changing position that is X0 Y0 Z90
x=probed_points[0][0];
y=probed_points[0][1];
macro("G0 X"+str(x)+" Y"+str(y)+" Z"+str(zp-z_safety+z_toolchange)+" F10000","ok",15,"Moving to Pos",0, warning=True,verbose=False)

#macro("G91","ok",2,"Relative mode",1, verbose=False)
#macro("G0 Z10 F1000","ok",3,"Moving away from touch point ",1,verbose=False )
#macro("G90","ok",2,"Abs_mode",1, verbose=False)

macro("M18","ok",2,"Motors off",0.5, warning=True, verbose=False)
macro("M746 S0","ok",2,"Disabling external probe",1, verbose=False)

#offset from the first calibration screw (lower left)
#probed_points=np.add(np.array(probed_points,screw_offset))

#DEBUG 
#print probed_points
#print "-----"

#Working too

#save everything
printlog()
macro("M300","ok",1,"Done!",1,verbose=False) #end print signal
#end
trace("Done!")
sys.exit()
