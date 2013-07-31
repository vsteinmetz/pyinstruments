"""
Implements the minimal wrapper around Ividotnet interop when the instrument 
is a spectrum analyzer. Mostly translates strange arrays by numpy arrays...
"""

from pyinstruments.drivers.ivi_interop.ividotnet import IviDotNetDriver
from pyinstruments.drivers.ivi_interop.ividotnet.dotnet_collections import \
                                        DotNetIntermediateCollection
from pyinstruments.wrappers import Wrapper
from pyinstruments.drivers.multiple_choice import MultipleChoice
from numpy import array
    
    

class IviDotNetSpecAn(IviDotNetDriver):
    """
    Implements the minimal wrapper around Ividotnet interop when the instrument 
    is a spectrum analyzer. Mostly translates strange arrays by numpy arrays...
    """
    
   # _supported_software_modules = ["AgXSAn"]
    
    def __init__(self, *args, **kwds):
        super(IviDotNetSpecAn, self).__init__(*args,**kwds)
    
    ivi_type = "IviSpecAn"


    @property
    def Traces(self):
        return DotNetIntermediateCollection(self._wrapped.Traces, self.Trace)
    

    class Trace(Wrapper):
        """wrapper for sub-object Trace"""
        
        def FetchY(self):
            """Fetches the existing curve, values are in dBm"""
            
            return array(tuple(self._wrapped.FetchY()))
            
        def FetchX(self):
            """Fetches the X-values for the curve.
            """
            
            return array(tuple(self._wrapped.FetchX()))
        

