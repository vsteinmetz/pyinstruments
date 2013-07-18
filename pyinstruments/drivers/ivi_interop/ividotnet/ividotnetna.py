"""
Implements the minimal wrapper around Ividotnet  interop when 
the instrument is a network analyzer. Since NA are not specifically
defined in the IVI specs, I use the AgNA (Agilent) conventions.
"""

from pyinstruments.drivers.ivi_interop.ividotnet import IviDotNetDriver
from pyinstruments.drivers.ivi_interop.ividotnet.dotnet_collections import \
                                        DotNetIntermediateCollection
from pyinstruments.wrappers import Wrapper
from numpy import array

class IviDotNetNA(IviDotNetDriver):
    """
    Implements the minimal wrapper around Ividotnet interop when the instrument 
    is a spectrum analyzer. Mostly translates strange arrays by numpy arrays...
    """
    
    _supported_software_modules = ["AgNA"]

    def instrument_type(self):
        """returns the type string, as in the Ivi specs"""
        return "NA"


    @property
    def Channels(self):
        return DotNetIntermediateCollection( \
                        self._wrapped.Channels, self.Channel)

    
    class Channel(Wrapper):
        
        @property
        def Measurements(self):
            return DotNetIntermediateCollection( \
                                self._wrapped.Measurements, \
                                self.Measurement)
        
        
        class Measurement(Wrapper):
            def FetchComplex(self):
                (dummy,re,im) = self._wrapped.FetchComplex(None,None)
                return array(tuple(re)) + 1j*array(tuple(im))
            
            def FetchMemoryComplex(self):
                (dummy,re,im) = self._wrapped.FetchMemoryComplex(None,None)
                return array(tuple(re)) + 1j*array(tuple(im))
            
            def FetchFormatted(self):
                re = self._wrapped.FetchFormatted()
                return array(tuple(re))
            
            def FetchMemoryFormatted(self):
                re = self._wrapped.FetchMemoryFormtted()
                return array(tuple(re))
        
            def FetchX(self):
                re = self._wrapped.FetchX()
                return array(tuple(re))
            
            def GetSParameter(self):
                (dummy, in_port, out_port) = self._wrapped.GetSParameter(0,0)
                return (in_port, out_port)
            
            