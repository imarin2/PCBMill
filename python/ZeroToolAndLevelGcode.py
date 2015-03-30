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
	
	gcode_file = str(sys.argv[5]);

	pointsFile = open(points_file, "r") 
	bedPoints=pointsFile.read()
	bed_measured_points = json.loads(bedPoints) #np.array(json.loads(bedPoints))
	probed_points=bed_measured_points[:-1] #all but last, because the dimensions are in the last
	
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
    
    out_file_trace = open(response_file,"a+")
    out_file.write(str(string) + "\n")
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

zeropoint=probed_points[0];

zp=zeropoint[2]+z_safety
x=zeropoint[0]
y=zeropoint[1]

trace("Zeroing this tool\r\n")

macro("G0 X"+str(x)+" Y"+str(y)+" Z"+str(zp)+" F10000","ok",15,"Moving to Pos",0, warning=True,verbose=False)

# probe with the new tool to set zero
serial.flushInput()
serial.write("G38\r\n")
probe_start_time = time.time()

data=""

while not data[:22]=="echo:endstops hit:  Z:":
   data=serial.readline().rstrip() 
   if (time.time() - probe_start_time>90):  #timeout management
   	trace("Touch probing failed")
        response("false")
        response("false")
	sys.exit("Can not touch the PCB")
        break   
   pass

# we do not actually care of the z touching value of this tool, we just want to set the zero.
#macro("G92 X0 Y0 Z0","ok",2,"Abs_mode",1, verbose=False)
macro("G90","ok",2,"Abs_mode",1, verbose=False)

trace("Leveling gcode file...\r\n")


response("true")
response("correctedfile.gcode")

trace("Done!")
sys.exit()
