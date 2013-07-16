"""
This package helps you interface instruments.

The driver layer is composed of 3 possible interfaces:
        - ivi_interop
        - visa
        - serial
        
If the driver is ivi-compliant, then it is embedded in an instrument which provides
basic graphical user interface capabilities.
"""

if __name__ == "__main__":
    from PyQt4.QtGui import QApplication as _qapplication
    _APP = _qapplication([]) ### should be done before importing clr and 
                             ### all that stuff to avoid an error message
    
from pyinstruments.factories import instrument,use_for_ivi
import pyinstruments.instruments

def gui():
    import pyinstruments.config.gui
    pyinstruments.config.gui.GUI.show()
    return pyinstruments.config.gui.GUI
    
if __name__ == "__main__":
    GUI = gui()
    _APP.exec_()