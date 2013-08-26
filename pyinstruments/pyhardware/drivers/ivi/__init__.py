"""
drivers using the ivi interop, including the sessionFactory and config_store
to instantiate and initialize the driver. These drivers are automatically
IVI-compliant.
"""

from pyivi import ivi_instrument, software_modules
from pyinstruments.pyhardware.drivers import Driver
from pyinstruments.utils.guiwrappersutils import GuiWrapper
from pyivi.ivicom.iviscope import ShortCutScope 

from PyQt4 import QtCore, QtGui



class IviDriver(Driver):
    _fields = []
    def __init__(self, pyivi_driver):
        self.driver = pyivi_driver

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

def add_fields(cls, list_of_names):
    cls._fields+=list_of_names
    for name in list_of_names:
        def getter(self, init_name=name):
            orig = self.driver.sc
            return orig.__getattribute__(init_name)
        def setter(self, val, init_name=name):
            orig = self.driver.sc
            setattr(orig, init_name, val)
            return val
        setattr(cls, name, property(getter, setter))

                    
class IviScopeDriver(IviDriver, GuiWrapper):
    specialized_name = 'IviScope'
    def __init__(self, pyividriver):
        super(IviScopeDriver, self).__init__(pyividriver)
        GuiWrapper.__init__(self)

    
    def _setupUi(self, widget):
        """sets up the graphical user interface"""
        
        widget._setup_vertical_layout()
        for field in self._fields:
            choices = None
            if hasattr(self.driver.sc, field + 's'):
                choices = self.driver.sc.__getattribute__(field + 's')
            widget._setup_gui_element(field, choices)
        widget._exit_layout()
        

add_fields(IviScopeDriver, [field[0] for field in ShortCutScope._fields])
add_fields(IviScopeDriver, [field[0] for field in ShortCutScope._channel_related_fields])
    


class IviSpecAnDriver(IviDriver, GuiWrapper):
    specialized_name = 'IviSpecAn'

class IviNADriver(IviDriver):
    specialized_name = ''

class IviFGenDriver(IviDriver):
    specialized_name = 'IviFgen'