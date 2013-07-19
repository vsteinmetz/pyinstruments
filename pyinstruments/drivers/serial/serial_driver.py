"""
Serial communication using the module "serial"
"""

from pyinstruments.drivers import Driver
import serial

class SerialDriver(Driver):
    """
    Base class for serial drivers
    """
    
    _supported_models = []
    lf = "\r\n"
    def __init__(self, \
                 logical_name, \
                 address, \
                 simulate, \
                 baudrate = 9600, \
                 bytesize = serial.SEVENBITS, \
                 parity = serial.PARITY_EVEN, \
                 stopbits = serial.STOPBITS_TWO, \
                 timeout= 0.5, \
                 dsrdtr = 0, \
                 xonxoff = 0):
        super(SerialDriver, self).__init__(logical_name, \
                                           address, \
                                           simulate)
        self.baudrate = baudrate
        self.bytesize = bytesize
        self.parity = parity
        self.stopbits = stopbits
        self.timeout = timeout
        self.dsrdtr = dsrdtr
        self.xonxoff = xonxoff
        
        self.serial = self.get_driver(port = self.address, \
                 baudrate = self.baudrate, \
                 bytesize = self.bytesize, \
                 parity = self.parity, \
                 stopbits = self.stopbits, \
                 timeout = self.timeout, \
                 dsrdtr = self.dsrdtr, \
                 xonxoff = self.xonxoff)
        
    def get_driver(self, **kwds):
        print kwds
        return serial.Serial(**kwds)

    def send(self, command):
        self.serial.write(command + self.lf)
        
    def readline(self):
        self.serial.readline()
    
    @classmethod
    def supported_models(cls):
        """
        returns the list of models supported by this driver. The
        model is the string between the first and second "," in the 
        *IDN? query reply.
        """
        
        return cls._supported_models