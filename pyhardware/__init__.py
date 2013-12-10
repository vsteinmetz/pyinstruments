"""
This package helps you interface instruments.

The driver layer is composed of 3 possible interfaces:
        - ivi_interop
        - visa
        - serial
        
If the driver is ivi-compliant, then it is embedded in an instrument which provides
basic graphical user interface capabilities.
"""

import curve

from guidata import qapplication as __qapplication
_APP = __qapplication()
_TITLE = "pyhardware"

def instrument(logical_name):
    from pyhardware.config import PyInstrumentsConfig as _PIC
    pic = _PIC()
    dic = pic[logical_name]
    address = str(dic["address"])
    model = dic["model"]
    simulate = dic["simulate"]
    code = dic["code"]
    exec(code)
    return instrument


def gui():
    import pyhardware.config.gui
    pyhardware.config.gui.GUI.show()
    return pyhardware.config.gui.GUI
    
if __name__ == "__main__":
    GUI = gui()
    _APP.exec_()