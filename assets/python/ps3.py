'''
Created on Mar 27, 2015

@author: tom
'''

import usb.core
import usb.util
import threading as th
import array

HID_GET_REPORT = 0x01
HID_SET_REPORT = 0x09
HID_REPORT_TYPE_INPUT = 0x01
HID_REPORT_TYPE_OUTPUT = 0x02

VID_SONY = 0x054c
PID_SIXAXIS = 0x0268


LED1 = 0x01
LED2 = 0x02
LED3 = 0x04
LED4 = 0x08
RUMBLE_HIGH = 0x10
RUMBLE_LOW = 0x20

class Ps3Com(object):
    '''
    Read from ps3 sixaxis remote
    '''


    def __init__(self):
        '''
        Constructor
        '''
        self.device = self._connect()
        

    def _connect(self):
        
        dev = usb.core.find(idProduct=PID_SIXAXIS, idVendor=VID_SONY)
        if dev is None:
            raise ValueError('Device not found')
        try:
            dev.detach_kernel_driver(0)
        except: 
            pass
  
        dev.set_configuration(1)
 
        setup_command = [0x42, 0x0c, 0x00, 0x00]
        dev.ctrl_transfer(usb.ENDPOINT_OUT | (0x01 << 5) | usb.RECIP_INTERFACE,
                                        HID_SET_REPORT,
                                        0x03f4,
                                        0,
                                        setup_command,
                                        100)
        return dev

    def read(self):
        '''Discard one read() to get current status'''
        self.device.read(0x81, 0x31, 0)
        return self.device.read(0x81, 0x31, 0)
            
    
#     a = array.array('B', (1,) * 0x31)
#     print a
    
  
            
    def getStatus(self):
        byteArray = self.read()
        buttonState = int(byteArray[2:4].tostring().encode('hex'), 16)
        status = {
            'ReportType' : byteArray[0],  # unsigned char ReportType;         //Report Type 01
#             
            'ButtonState' : buttonState,  # unsigned int  ButtonState;        // Main buttons
            'ButtonUp' : (buttonState & 0x1000) > 0,
            'ButtonDown' : (buttonState & 0x4000) > 0,
            'ButtonLeft' : (buttonState & 0x8000) > 0,
            'ButtonRight' : (buttonState & 0x2000) > 0,
            'ButtonL1' : (buttonState & 0x4) > 0,
            'ButtonL2' : (buttonState & 0x1) > 0,
            'ButtonR1' : (buttonState & 0x8) > 0,
            'ButtonR2' : (buttonState & 0x2) > 0,
            'ButtonSelect' : (buttonState & 0x100) > 0,
            'ButtonStart' : (buttonState & 0x800) > 0,
            'ButtonLeftJoy' : (buttonState & 0x200) > 0,
            'ButtonRightJoy' : (buttonState & 0x400) > 0,
            'ButtonTriangle' : (buttonState & 0x10) > 0,
            'ButtonSquare' : (buttonState & 0x80) > 0,
            'ButtonCross' : (buttonState & 0x40) > 0,
            'ButtonCircle' : (buttonState & 0x20) > 0,
            'ButtonPs' : (byteArray[4] & 0x1) > 0,  #       // PS button
#          
            'LeftStickX' : byteArray[6],  # // left Joystick X axis 0 - 255, 128 is mid
            'LeftStickY' : byteArray[7],  # // left Joystick Y axis 0 - 255, 128 is mid
            'RightStickX' : byteArray[8],  # // right Joystick X axis 0 - 255, 128 is mid
            'RightStickY' : byteArray[9],  # // right Joystick Y axis 0 - 255, 128 is mid
#           
            'PressureUp' : byteArray[14],  # // digital Pad Up button Pressure 0 - 255
            'PressureRight' : byteArray[15],  # // digital Pad Right button Pressure 0 - 255
            'PressureDown' : byteArray[16],  # // digital Pad Down button Pressure 0 - 255
            'PressureLeft' : byteArray[17],  # // digital Pad Left button Pressure 0 - 255
            'PressureL2' : byteArray[18],  # // digital Pad L2 button Pressure 0 - 255
            'PressureR2' : byteArray[19],  # // digital Pad R2 button Pressure 0 - 255
            'PressureL1' : byteArray[20],  # // digital Pad L1 button Pressure 0 - 255
            'PressureR1' : byteArray[21],  # // digital Pad R1 button Pressure 0 - 255
            'PressureTriangle' : byteArray[22],  # // digital Pad Triangle button Pressure 0 - 255
            'PressureCircle' : byteArray[23],  # // digital Pad Circle button Pressure 0 - 255
            'PressureCross' : byteArray[24],  # // digital Pad Cross button Pressure 0 - 255
            'PressureSquare' : byteArray[25],  # // digital Pad Square button Pressure 0 - 255
#         
            'Charge' : byteArray[29],  # // charging status ? 02 : charge, 03 : normal
            'Power' : byteArray[30],  # // Battery status
            'Connection' : byteArray[31],  # // Connection Type
#          
            'AccelerometerX' : int(byteArray[41:43].tostring().encode('hex'), 16),  # // X axis accelerometer Big Endian 0 - 1023
            'AccelerometerY' : int(byteArray[43:45].tostring().encode('hex'), 16),  #       // Y axis accelerometer Big Endian 0 - 1023
            'AccelerometerZ' : int(byteArray[45:47].tostring().encode('hex'), 16),  # // Z axis accelerometer Big Endian 0 - 1023
            'GyrometerX' : int(byteArray[47:49].tostring().encode('hex'), 16),  # // Z axis Gyro Big Endian 0 - 1023
            }
        
        return status
        
    
    def set_led_and_rumble(self, param):
        control_packet = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                             0x00, 0x02, 0xFF, 0x27, 0x10, 0x10, 0x32, 0xFF,
                             0x27, 0x10, 0x00, 0x32, 0xFF, 0x27, 0x10, 0x00,
                             0x32, 0xFF, 0x27, 0x10, 0x00, 0x32, 0x00, 0x00,
                             0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                             0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
        
        ''' LED settings '''
        control_packet[9] = (param & 0x0F) << 1
        '''/* Rumble settings */'''
        if(param & 0x30):
            control_packet[1] = control_packet[3] = 0xFE
            if(param & 0x10):  # //High rumble
                control_packet[4] = 0xFF
            else:  # //Low rumble
                control_packet[2] = 0xFF
            
        return self.device.ctrl_transfer(usb.ENDPOINT_OUT | (0x01 << 5) | usb.RECIP_INTERFACE,
                                        HID_SET_REPORT,
                                        0x0201,
                                        0,
                                        control_packet,
                                        100)


