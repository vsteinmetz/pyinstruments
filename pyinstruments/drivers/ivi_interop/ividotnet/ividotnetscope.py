"""
Implements the minimal wrapper around Ividotnet interop when the instrument 
is a scope. Mostly translates strange arrays by numpy arrays...
"""

from pyinstruments.drivers.ivi_interop.ividotnet import IviDotNetDriver
from pyinstruments.drivers.ivi_interop.ividotnet.dotnet_collections import \
                                        DotNetIntermediateCollection
from pyinstruments.wrappers import Wrapper
from numpy import array

class IviDotNetScope(IviDotNetDriver):
    """
    Implements the minimal wrapper around Ividotnet interop when the instrument 
    is a scope. Mostly translates strange arrays by numpy arrays...
    """
    
    _supported_software_modules =  ["Tkdpo2k3k4k", \
                                   "lcscope", \
                                   "TekScope", \
                                   "AgInfiniiVision"]
    
    def instrument_type(self):
        """returns the type string as in the Ivi specs"""
        return "Scope"
    
    @property
    def Channels(self):
        return DotNetIntermediateCollection(self._wrapped.Channels, self.Channel)
    
    class Channel(Wrapper):
        """wrapper for sub-object Channel"""
    
        _direct_from_driver = "__all__"
            
        def FetchWaveform(self):
            """Fetches the existing curve
            """
            
            if not self.Enabled:
                raise ValueError("Channel is currently disabled")
            (dummy, dat, start, step) = self._wrapped.FetchWaveform(None,\
                                                                     0,\
                                                                      0)
            return array(tuple(dat)), start, step