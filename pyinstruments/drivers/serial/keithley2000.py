import serial
import sys
import time
from pyinstruments.drivers.serial import SerialDriver


class Keithley2000(SerialDriver):
    """
    Driver for the multimeter Keithley2000
    """
    
    _supported_models = ["Keithley2000"]

    def __init__(self, *args):
        kwds = {"baudrate" : 4800, \
                "bytesize" : serial.EIGHTBITS, \
                "parity" : serial.PARITY_NONE, \
                "stopbits" : serial.STOPBITS_ONE, \
                "timeout" : 0.5, \
                "xonxoff" : True}
        super(Keithley2000, self).__init__(*args, **kwds)
        #print self.serial
        self.send("*IDN?")
        print "DEVICE: " + self.ser.readline()
        self.send("*RST")
        self.send("*CLS")
        

    def set4ResistanceMeasurement(self, mrange = 100000):
        self.measrange = mrange
        self.send("SYSTem:REMote")
        self.send("DISPLAY:TEXT \"Measuring...\" ")
        self.send("CONF:FRES " + str(mrange))
        self.send("TRIGGER:SOURCe IMMediate")
        self.send("TRIGGER:DELay:AUTO ON")

    def end4ResistanceMeasurement(self): 
        self.send("DISPLAY:TEXT:CLEAR")
        self.send("*CLS")
        self.send("SYST:LOCAL")
        
    def getValue(self): 
        self.send("READ?")
        time.sleep(0.1)
        res = self.readline()
        return float(res.strip())

if __name__ == "__main__":
    ea = Keithley2000(sys.argv[1])
