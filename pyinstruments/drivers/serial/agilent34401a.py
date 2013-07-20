import serial
import sys
import time
from pyinstruments.drivers.serial import SerialDriver

class Agilent34401A(SerialDriver):
    _supported_models = ["34401A"]
    measrange = 100000

    def __init__(self,*args,**kwds):
        kwds = {"baudrate" : 9600, \
                "bytesize" : serial.SEVENBITS, \
                "parity" : serial.PARITY_EVEN, \
                "stopbits" : serial.STOPBITS_TWO, \
                "timeout" : 0.5, \
                "dsrdtr" : True}
        super(Agilent34401A,self).__init__(*args, **kwds)
        #self.ser = serial.Serial(port = device, baudrate = 9600, bytesize = serial.SEVENBITS, parity = serial.PARITY_EVEN, stopbits = serial.STOPBITS_TWO, timeout= 0.5, dsrdtr = 1)
        #print self.ser
        self.send("*IDN?")
        print "DEVICE: " + self.ser.readline()
        self.send("*RST")
        self.send("*CLS")


    def setResistanceMeasurement(self, mrange = 100000):
        self.measrange = mrange
        self.send("SYSTem:REMote")
        self.send("DISPLAY:TEXT \"Measuring...\" ")
        self.send("CONF:FRES " + str(self.measrange))
        self.send("TRIGGER:SOURCe IMMediate")
        self.send("TRIGGER:DELay:AUTO ON")
#        time.sleep(0.1)

    def endResistanceMeasurement(self): 
        self.send("DISPLAY:TEXT:CLEAR")
        self.send("*CLS")
        self.send("SYST:LOCAL")
        
    def getValue(self): 
        self.send("READ?")
        time.sleep(0.1)
        res = self.ser.readline()
        print "Resistance = " + res
        return float(res.strip())

if __name__ == "__main__":
    ea = Agilent34401A(sys.argv[1])