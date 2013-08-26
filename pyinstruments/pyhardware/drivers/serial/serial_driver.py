"""
Serial communication using the module "serial"
"""

from pyinstruments.pyhardware.drivers import Driver
import serial

class SerialDriver(Driver):
    """
    Base class for serial drivers
    """
    
    lf = "\r\n"
    def __init__(self, \
                 logical_name, \
                 address, \
                 simulate, \
                 baudrate = 9600, \
                 bytesize = serial.EIGHTBITS, \
                 parity = serial.PARITY_NONE, \
                 stopbits = serial.STOPBITS_ONE, \
                 timeout= 1, \
                 dsrdtr = False, \
                 xonxoff = False,
                 rtscts = False):
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
        self.rtscts = rtscts
        
        self.serial = self.get_driver(port = self.address, \
                 baudrate = self.baudrate, \
                 bytesize = self.bytesize, \
                 parity = self.parity, \
                 stopbits = self.stopbits, \
                 timeout = self.timeout, \
                 dsrdtr = self.dsrdtr, \
                 xonxoff = self.xonxoff, \
                 rtscts = self.rtscts)
        
    def get_driver(self, **kwds):
        return serial.Serial(**kwds)

    def send(self, command):
        self.serial.write(command + self.lf)
        
    def send_rawdata(self, command):    
        self.serial.write(command)
        
    def readline(self):
        return self.serial.readline()
    
    def close(self):
        self.serial.close()

    def open(self):
        self.serial = self.get_driver(port = self.address, \
                 baudrate = self.baudrate, \
                 bytesize = self.bytesize, \
                 parity = self.parity, \
                 stopbits = self.stopbits, \
                 timeout = self.timeout, \
                 dsrdtr = self.dsrdtr, \
                 xonxoff = self.xonxoff, \
                 rtscts = self.rtscts)
        return True

    def ask(self, command = ""):
        if command != "":
            self.send(command)
        return (self.readline().strip())
    
    @classmethod
    def supported_models(cls):
        """
        returns the list of models supported by this driver. The
        model is the string between the first and second "," in the 
        *IDN? query reply.
        """
        
        models = []
        if hasattr(cls, '_supported_models'):
            return cls._supported_models
        for child in cls.__subclasses__():
            models+=child.supported_models()
        return models