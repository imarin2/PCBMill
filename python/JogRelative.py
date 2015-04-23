import time
import sys, os
import serial
from subprocess import call
import numpy as np
import json
import pprint
import CNC

global start_time
global x_coord, y_coord

start_time = time.time()

#Args
try:
	log_file=str(sys.argv[1]) #param for the log file
	log_trace=str(sys.argv[2])	#trace log file
	x_coord = sys.argv[3]
	y_coord = sys.argv[4]
	z_coord = sys.argv[5]
	
except:
	print "Missing Log reference"
	trace("Missing Parameters!")
	sys.exit()


#num of probes each point

s_warning=s_error=s_skipped=0

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

trace("Jogging to position...")
port = '/dev/ttyAMA0'
baud = 115200

#initialize serial
serial = serial.Serial(port, baud, timeout=0.6)
serial.flushInput()

macro("G91","ok",2,"Relative mode",0, verbose=False)
macro("G0 X"+str(x_coord)+" Y"+str(y_coord)+" Z"+str(z_coord)+" F10000","ok",15,"Moving to Pos",0, warning=True,verbose=False)
macro("G90","ok",2,"Abs_mode",0, verbose=False)
	
response("true")
trace("Done!")
sys.exit()
