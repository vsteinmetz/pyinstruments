"""
drivers using the ivi interop, including the sessionFactory and config_store
to instantiate and initialize the driver. These drivers are automatically
IVI-compliant.
"""

from pyivi import ivi_instrument, software_modules
from pyinstruments.pyhardware.drivers import Driver

from PyQt4 import QtCore, QtGui

class IviDriver(Driver):
    def __init__(self, pyivi_driver):
        self.pyivi_driver = pyivi_driver

    @classmethod
    def supported_models(cls):
        models = []
        if not hasattr(cls, "specialized_name"):
            for child in cls.__subclasses__():
                models+=child.supported_models()
            return models
        for soft_mod in [software_modules[smn] for smn \
                         in cls.supported_software_modules()]:
            models+=soft_mod.supported_instrument_models()
        return models

    @classmethod
    def supported_software_modules(cls):
        if not hasattr(cls, "specialized_name"):
            return []
        modules = []
        for module_name, module in software_modules.iteritems():
            if cls.specialized_name in module.c_apis or \
                cls.specialized_name in module.com_apis:
                modules.append(module_name)
        return modules
                    
class IviScopeDriver(IviDriver):
    specialized_name = 'IviScope'
    
    def gui(self):
        return QtGui.QPushButton('hello')

class IviSpecAnDriver(IviDriver):
    specialized_name = 'IviSpecAn'

class IviNADriver(IviDriver):
    specialized_name = ''

class IviFGenDriver(IviDriver):
    specialized_name = 'IviFgen'