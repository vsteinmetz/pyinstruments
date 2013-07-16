"""
defines the base class for a driver. This abstract class can be inherited by 
ivicom, ividotnet, visa or serial
"""

class Driver(object):
    """Base class to interface an instrument
    """
    
    def __init__(self, logical_name, address, simulate):
        self.logical_name = logical_name
        self.address = address
        self.simulate = simulate
        
    def is_ivi_instrument(self):
        """returns True if the driver complies with ivi specification, 
        False otherwise. A visa or serial driver could be ivi-compliant !"""    
        
        return False
            
    def instrument_type(self):
        """gives the instrument type ("scope", "spec_an", "na" ...)"""
        
        raise NotImplementedError()        
    
    @classmethod
    def supports(cls, model):
        """given a model string, returns True if instrument is supported,
         False otherwise
         """
         
        raise NotImplementedError()