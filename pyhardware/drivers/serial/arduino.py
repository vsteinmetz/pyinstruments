#Copyright (c) 2009-2010 Akash Manohar J <akash@akash.im>

import serial
import sys
import time
from pyhardware.drivers.serial import SerialDriver


class Arduino(SerialDriver):
    """
    Driver for the Arduino UNO
    """
    
    _supported_models = ["Arduino UNO"]

    __OUTPUT_PINS = -1

    def __init__(self, *args):
        kwds = {"baudrate" : 115200, \
                "timeout" : 0.5}
        super(Arduino, self).__init__(*args, **kwds)
        #print self.serial
        self.send_rawdata('99')
        
    def output(self, pinArray):
        self.__sendData('5')
        self.__sendData(len(pinArray))
        if(isinstance(pinArray, list) or isinstance(pinArray, tuple)):
            self.__OUTPUT_PINS = pinArray
            for each_pin in pinArray:
                self.__sendData(each_pin)
        return True

    def outputAll(self):
        self.output(range(14))
        return True
    
    def set(self, pin, val):
        if val:
            self.setHigh(pin)
        else:
            self.setLow(pin)
        #else:
        #    print "Error, val must be boolean"    
        
    def setLow(self, pin):
        self.__sendData('0')
        self.__sendData(pin)
        return True

    def setHigh(self, pin):
        self.__sendData('1')
        self.__sendData(pin)
        return True

    def getState(self, pin):
        self.__sendData('2')
        self.__sendData(pin)
        return self.__formatPinState(self.__getData()[0])

    def analogWrite(self, pin, value):
        self.__sendData('3')
        self.__sendData(pin)
        self.__sendData(value)
        return True

    def analogRead(self, pin):
        self.__sendData('4')
        self.__sendData(pin)
        return self.__getData()

    def blink(self, pin):
        for i in range(10):
            self.setHigh(pin)
            time.sleep(0.2)
            self.setLow(pin)
            time.sleep(0.2)
        
    def turnOff(self):
        for each_pin in self.__OUTPUT_PINS:
            self.setLow(each_pin)
        return True

    def __sendData(self, serial_data):
        data = 'r'
        while(len(data) > 0 and data[0] != "w"):
            data = self.__getData()
        self.serial.write(str(serial_data))

    def __getData(self):
        return self.serial.readline().rstrip('\n')

    def __formatPinState(self, pinValue):
        if pinValue == '1':
            return True
        else:
            return False

    def close(self):
        self.serial.close()
        return True

if __name__ == "__main__":
    ea = Arduino(sys.argv[1])




class ArduinoLockbox(Arduino):
    """
    Driver for the Arduino UNO Lockbox
    """
    class Channel(object):
        def __init__(self, arduino, pins):
            self.pins = pins
            self.arduino = arduino
                   
        @property
        def inverse(self):
            return self.arduino.getState(self.pins['inverse'])
        
        @inverse.setter
        def inverse(self, val):
            self.arduino.set(self.pins['inverse'], val)
            
        @property
        def triangle(self):
            return self.arduino.getState(self.pins['triangle'])
        
        @triangle.setter
        def triangle(self, val):
            self.arduino.set(self.pins['triangle'], val)
    
        @property
        def i1(self):
            return self.arduino.getState(self.pins['i1'])
        
        @i1.setter
        def i1(self, val):
            self.arduino.set(self.pins['i1'], val)
        
        @property
        def i2(self):
            return self.arduino.getState(self.pins['i2'])
        
        @i2.setter
        def i2(self, val):
            self.arduino.set(self.pins['i2'], val)
       
        @property
        def i3(self):
            return self.arduino.getState(self.pins['i3'])
        
        @i3.setter
        def i3(self, val):
            self.arduino.set(self.pins['i3'], val)
       
    def __init__(self,*args,**kwds):
        super(ArduinoLockbox,self).__init__(*args,**kwds)
        self.slow = self.Channel(self,dict(inverse = 2, triangle = 3, i3 = 4, i2 = 5, i1 = 6))
        self.fast = self.Channel(self,dict(inverse = 10, triangle = 13, i3 = 8, i2 = 12, i1 = 11))
        '''i3 is not present in this the fast part of this lockbox'''
        self.outputAll()
        time.sleep(0.1)
        '''there is an error in the initial communication; we need to cal outputAll twice'''
        self.outputAll()
        