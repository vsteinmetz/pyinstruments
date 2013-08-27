from pyinstruments.utils.guiwrappersutils import GuiWrapper
from pyinstruments.pyhardware.drivers import Driver

from pyivi.ivicom.iviscope import ShortCutScope
from pyivi import software_modules

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

def add_fields(cls, list_of_names, add_ref=True):
    if add_ref:
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
