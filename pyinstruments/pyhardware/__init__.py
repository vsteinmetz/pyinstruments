"""
This package helps you interface instruments.

The driver layer is composed of 3 possible interfaces:
        - ivi_interop
        - visa
        - serial
        
If the driver is ivi-compliant, then it is embedded in an instrument which provides
basic graphical user interface capabilities.
"""

from pyinstruments.utils import curve

from guidata import qapplication as __qapplication
_APP = __qapplication()

from pyinstruments.pyhardware.config import PyInstrumentsConfig as _PIC
    
def instrument(logical_name):
    pic = _PIC()
    dic = pic[logical_name]
    address = dic["address"]
    model = dic["model"]
    simulate = dic["simulate"]
    code = dic["code"]
    exec(code)
    return instrument


def gui():
    import pyinstruments.pyhardware.config.gui
    pyinstruments.pyhardware.config.gui.GUI.show()
    return pyinstruments.pyhardware.config.gui.GUI
    
if __name__ == "__main__":
    GUI = gui()
    _APP.exec_()