"""
This module defines 2 different factories :
    - driver_factory(model): given a model string, returns the appropriate
    driver
    - instrument_factory(driver): given a driver, returns the appropriate
    instrument
"""

from pyinstruments.drivers import Driver
from pyinstruments.drivers.ivi_interop import IviInteropDriver
from pyinstruments.factories.factories_utils import list_all_child_classes    
from pyinstruments.config import PyInstrumentsConfig

USE_FOR_IVI = dict()

def use_for_ivi(instrument_type_str):
    """Use this decorator to set the class that has to be used for each type
    of ivi_driver. instrument_type_str can be "scope", "spec_an", "na" ..."""

    def func(cls):
        """wrapper function, just register the class in the global variable 
        pyinstruments.factories.USE_FOR_IVI
        """
        
        USE_FOR_IVI[instrument_type_str] = cls
        return cls
    return func
        
def driver_factory(model):
    """given a model string, returns the appropriate driver"""
  
    dictionnary = list_all_child_classes(Driver)
    
    for driver in dictionnary.values():
        try:
            if model in driver.supported_models():
                try:
                    software_module = driver.get_software_module(model)
                except AttributeError:
                    software_module = None
                return (driver, software_module)
        except NotImplementedError:
            pass
        
def _driver(model, logical_name, address, simulate):
    """returns the driver corresponding to the model, allready initialized"""
    (driv, software_module) = driver_factory(model)
    if issubclass(driv, IviInteropDriver):
        return driv("pyinstruments_" + software_module, \
                     logical_name, \
                     address, \
                     simulate)
    else:
        return driv(logical_name, address, simulate)    

def driver(logical_name):
    """uses the module config to determine the values of "model", "address" 
    and "simulate" from the 'logical_name" and returns the best driver, 
    initialized with the instrument.
    """
    
    pic = PyInstrumentsConfig()
    dic = pic[logical_name]
    address = dic["address"]
    model = dic["model"]
    simulate = dic["simulate"]
    return _driver(model, logical_name, address, simulate)
    
def _instrument_factory(driver):
    """Takes a driver and wrapps the appropriate instrument 
    around, using the convention:
            if driver.is_ivi_instrument():
                returns the ivi_gui_instrument corresponding to
                driver.instrument_type()
            else:
                no wrapper...
    """
    
    if not driver.is_ivi_instrument():
        return driver
    else:
        return USE_FOR_IVI[driver.instrument_type()]


def instrument_factory(logical_name):
    """
    returns the non-instanciated class for the instrument.
    """
    
    pic = PyInstrumentsConfig()
    dic = pic[logical_name]
    address = dic["address"]
    model = dic["model"]
    simulate = dic["simulate"]
    driver, mod = driver_factory(model)
    instrument_driver = _instrument_factory(driver)    
    return instrument_driver
    
def instrument(logical_name):
    """
    step 1/
    uses the module config to determine the values of "model", "address" 
    and "simulate" from the logical_name. Use pyinstruments.gui() to display
    an overview of the available logical names and edit them
    
    step 2/
    guesses the best driver for the found model and initializes it with
    the instrument:
    
            if driver.is_ivi_instrument():
                returns the ivi_wrapper listed in 
                pyinstruments.factories.USE_FOR_IVI[driver.instrument_type()]
                
                (define your own class with the decorator
                pyinstruments.use_for_ivi(ivi_type_str) 
                to have your own class registered.)
                
            else:
                returns the raw driver
    """
    
    driv = driver(logical_name)
    return instrument_factory(logical_name)(driv)