#Copyright (c) 2009-2010 Akash Manohar J <akash@akash.im>

import serial
import sys
import time
from pyinstruments.drivers.serial import SerialDriver


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
        self.__sendData(len(pinArray))

        if(isinstance(pinArray, list) or isinstance(pinArray, tuple)):
            self.__OUTPUT_PINS = pinArray
            for each_pin in pinArray:
                self.__sendData(each_pin)
        return True
    
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

    def turnOff(self):
        for each_pin in self.__OUTPUT_PINS:
            self.setLow(each_pin)
        return True

    def __sendData(self, serial_data):
        while(self.__getData()[0] != "w"):
            pass
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

