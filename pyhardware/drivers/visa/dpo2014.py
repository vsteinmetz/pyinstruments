"""module to interface the DPO3014 scope (using VISA interface)"""

from pyhardware.drivers.visa.dpo3014 import DPO3014

class DPO2014(DPO3014):
    _supported_models = ["DPO2014"]