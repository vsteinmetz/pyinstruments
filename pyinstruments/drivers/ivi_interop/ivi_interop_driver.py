"""
Basic class for driver communication with an instrument using ivi_interop
framework
"""

from pyinstruments.drivers import Driver
from pyinstruments.wrappers import Wrapper

class IviInteropDriver(Driver, Wrapper):
    """
    Base class for IviDotNetDriver and IviComDriver
    """
    
    def __init__(self, software_module, *args):
        """
        args are logical_name, address, simulate
        """
        
        self.software_module = software_module
        super(IviInteropDriver, self).__init__(*args)
        Wrapper.__init__(self, self.get_driver())
        
    def is_ivi_instrument(self):
        """instruments interfaced in this way are expected to be IVI
        compliant"""
        
        return True
        
    @classmethod
    def get_software_module(cls, model):
        """
        given the model name,  returns the string corresponding to the 
        supporting software_module
        """
        
        raise NotImplementedError("should be implemented in child classes")