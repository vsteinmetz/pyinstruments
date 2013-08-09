"""
This module defines 2 different factories :
    - driver_factory(model): given a model string, returns the appropriate
    driver
    - instrument_factory(driver): given a driver, returns the appropriate
    instrument
"""

from pyinstruments.pyhardware.factories.factories import   driver_factory, \
                                                driver, \
                                                instrument_factory, \
                                                instrument, \
                                                use_for_ivi, \
                                                USE_FOR_IVI