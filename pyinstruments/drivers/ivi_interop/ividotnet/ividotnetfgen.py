"""
Implements the minimal wrapper around Ividotnet interop when the instrument 
is a scope. Mostly translates strange arrays by numpy arrays...
"""

from pyinstruments.drivers.ivi_interop.ividotnet import IviDotNetDriver
from pyinstruments.drivers.ivi_interop.ividotnet.dotnet_collections import \
                                        DotNetIntermediateCollection
from pyinstruments.wrappers import Wrapper
from numpy import array

class IviDotNetFgen(IviDotNetDriver):
    """
    Implements the minimal wrapper around Ividotnet interop when the instrument 
    is a scope. Mostly translates strange arrays by numpy arrays...
    """
 
    #_supported_software_modules =  ["33220A"]
    ivi_type = "IviFgen"
    
