'''
Created on Apr 8, 2015

@author: tom
'''

from json import JSONDecoder
import time

class FabJoyFunctions(object):
    '''
    A collection of registered joystick functions
    '''
    
    functionList = {'joystick':{
#                                 'xAxis'         : ('Move head in x-direction', False),
#                                 'yAxis'         : ('Move head in y-direction', False),
#                                 'zAxis'         : ('Move head in z-direction', False),
                                'eAxis'         : ('Extruder', True),
                                'notUsed'       : ('Joystick not used', False)
                                },
                    'discrete':{
                                'zProbe'        : ('Lower and raise z-probe', False),
                                'incFeedRate'   : ('Increase Feedrate', True),
                                'decFeedrate'   : ('Decrease Feedrate', True),
                                'reset'         : ('Reset safety stop', False),
                                'setZero'       : ('Set Zero position', False),
                                'gotoZero'      : ('Go to Zero position', True),
                                'notUsed'       : ('Button not used', False)
                                },
                    'analog'  :{
                                'eAxisFwd'      : ('Extruder Forward', True),
                                'eAxisRev'      : ('Extruder Reverse', True)
                                }
                    }


    def __init__(self, serialPort, console):
        self.serialPort = serialPort
        self.console = console
        self.activeFunctions = {}
        self._setupFunctions()
        self.feedRateOverride = 1.0
        
    
    def _setupFunctions(self):
        f = open('/var/www/fabui/application/plugins/joystickjog/assets/python/jsbuttons.json', 'r')
        fc = f.read()
        jsonD = JSONDecoder()
        funcDict = jsonD.decode(fc)
        f.close()
        
        for key, value in funcDict.iteritems():
            if value['function'] != 'notUsed' and value['function'] != '':
                self.activeFunctions[key] = value
    
    
    def _axisScale(self, val, span=255, deadband=20):
        tmp = val - (span / 2.0)
        if (abs(tmp) < deadband):
            return 0.0
        else:
            scaledVal = (abs(tmp) - deadband) / float((span / 2.0) - deadband)
            if tmp < 0:
                scaledVal *= -1
            return scaledVal
            
    def _calculateGcode(self, jStatus, gain = 1.0):
        
        xSpeed = self._axisScale(jStatus['LeftStickX'])
        ySpeed = -self._axisScale(jStatus['LeftStickY'])
        zSpeed = self._axisScale(jStatus['RightStickY'])
        xyGain = 1.0 * gain
        zGain = 0.3 * gain
        feedRateGain = 3000.0 * gain
        
        gCode = 'G0 '
        gCode += 'X%0.3f ' % (xSpeed * xyGain)
        gCode += 'Y%0.3f ' % (ySpeed * xyGain)
        gCode += 'Z%0.3f ' % (zSpeed * zGain)
        gCode += 'F%0.0f' % (max((abs(xSpeed), abs(ySpeed), abs(zSpeed))) * feedRateGain)
        
        move = max((abs(xSpeed), abs(ySpeed), abs(zSpeed))) > 0.0
        
        return gCode, move
            
    def callFunctions(self, jsStatus):
        gCode, move = self._calculateGcode(jsStatus, self.feedRateOverride)
    
        if move:
            self.serialPort.write(gCode + "\r\n")
            self.serialPort.readline().rstrip()
            self.console.updatePosition(self.console.stringToPos(gCode))
            return
        
        for key, value in self.activeFunctions.iteritems():
            if 'analog' in value['type']:
                discreteValue = jsStatus[key]
                analogValue = jsStatus[key.replace('Button', 'Pressure')]
            elif 'joystick' in value['type']:
                discreteValue = False
                analogValue = jsStatus[key]
            else:
                discreteValue = jsStatus[key]
                analogValue = 0
            getattr(self, value['function'])(discreteValue, analogValue, value['param'])
    
    
    '''Selectable functions below '''                
#     def xAxis(self, dVal, aVal, param):
#         pass
#     
#     def yAxis(self, dVal, aVal, param):
#         pass
#     
#     def zAxis(self, dVal, aVal, param):
#         pass
    
    def eAxis(self, dVal, aVal, param):
        pass
    
    def eAxisFwd(self, dVal, aVal, param):
        if aVal > 0:
            self.console.setAppendString('E-axis Forward')
            try:
                param = float(param)
                if not 10.0 <= param <= 1000.0:
                    param = 500.0
            except:
                param = 500.0
            
            feedrate = (aVal/255.0) * param
            feed = (aVal/255.0) * (param/500.0) * 10.0
            self.serialPort.write("G0 E%0.3f F%0.0f\r\n" % (feed, feedrate))
            self.serialPort.readall()    
            
    def eAxisRev(self, dVal, aVal, param):
        if aVal > 0:
            self.console.setAppendString('E-axis Reverse')
            try:
                param = float(param)
                if not 10.0 <= param <= 1000.0:
                    param = 500.0
            except:
                param = 500.0
            
            feedrate = (aVal/255.0) * param
            feed = (aVal/255.0) * (param/500.0) * 10.0
            self.serialPort.write("G0 E-%0.3f F%0.0f\r\n" % (feed, feedrate))
            self.serialPort.readall()
    
    zProbeDown = False
    zProbeMem = False
    def zProbe(self, dVal, aVal, param):
        if dVal and not self.zProbeMem:
            self.zProbeMem = True
            if not self.zProbeDown:
                self.serialPort.write("M401\r\n")
                self.serialPort.readall()
                self.zProbeDown = True
                self.console.setAppendString('Z-Probe Down')
            else:
                self.serialPort.write("M402\r\n")
                self.serialPort.readall()
                self.zProbeDown = False
                self.console.setAppendString('Z-Probe Up')
        elif not dVal and self.zProbeMem:
            self.zProbeMem = False

    def reset(self, dVal, aVal, param):
        if dVal:
            self.serialPort.write("M999\r\n")
            self.serialPort.readall() 
            self.console.setAppendString('Reset safety warning')
            
    def incFeedRate(self, dVal, aVal, param):
        if dVal:
            try:
                step = float(param) / 100.0
            except:
                step = 0.05
                
            self.feedRateOverride += step
            if self.feedRateOverride > 2.0:
                self.feedRateOverride = 2.0
            
            self.console.setAppendString('Speed: %0.0f%s' % (self.feedRateOverride*100, '%'))
            time.sleep(0.5)
           
    def decFeedRate(self, dVal, aVal, param):
        if dVal:
            try:
                step = float(param) / 100.0
            except:
                step = 0.05
             
            self.feedRateOverride -= step
            if self.feedRateOverride < 0.0:
                self.feedRateOverride = 0.0
            
            self.console.setAppendString('Speed: %0.0f%s' % (self.feedRateOverride*100, '%'))
            time.sleep(0.5)
       
    def setZero(self, dVal, aVal, param):
        if dVal:
            self.console.setAppendString('Set Zero position')
            self.serialPort.write("G92 X0 Y0 Z0\r\n")
            self.serialPort.readall() 
            
            
            self.serialPort.write("M114\r\n")
            self.console.setPostition(self.console.stringToPos(self.serialPort.readall().rstrip()))

    def gotoZero(self, dVal, aVal, param):
        if dVal:
            try:
                param = float(param)
                if not 100.0 <= param <= 5000.0:
                    param = 3000.0
            except:
                param = 3000.0
                
            self.console.setAppendString('Goto zero position')
            self.serialPort.write("G90\r\n")
            self.serialPort.readall()
            self.serialPort.write("G0 X0 Y0 Z0 F%0.0f\r\n" % (param,))
            self.serialPort.readall() 
            self.serialPort.write("G91\r\n")
            self.serialPort.readall()
            
            
            self.serialPort.write("M114\r\n")
            self.console.setPostition(self.console.stringToPos(self.serialPort.readall().rstrip()))
    
    def notUsed(self, dVal, aVal, param):
        pass