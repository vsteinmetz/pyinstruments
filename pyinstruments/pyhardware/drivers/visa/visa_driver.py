"""
Visa communication using the module "visa"
"""

from pyinstruments.pyhardware.drivers import Driver
import visa

class VisaDriver(Driver):
    """
    Base class for device interfaced with Visa
    """
    _supported_models = []
    
    def __init__(self, *args):
        """
        args are logical_name, address, simulate
        """
        
        super(VisaDriver, self).__init__(*args)
        self.visa_instr = visa.instrument(self.address)
        
        
    def ask(self, val):
        """
        Asks the driver
        """
        
        return self.visa_instr.ask(val)
    
    def read(self):
        """
        reads a value
        """
        
        return self.visa_instr.read()
    
    def write(self, val):
        """
        writes a value
        """
        
        return self.visa_instr.write(val)
    
    @classmethod
    def supported_models(cls):
        """
        returns the list of models supported by this driver. The
        model is the string between the first and second "," in the 
        *IDN? query reply.
        """
        
        return cls._supported_models