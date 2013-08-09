"""
Instruments that offer the possibility to display a Graphical User Interface
"""

from pyinstruments.pyhardware.instruments import MenuItem
from pyinstruments.pyhardware.instruments.ivi_instrument import IviInstrument
from pyinstruments.utils.guiwrappersutils import GuiWrapper

from PyQt4 import QtCore, QtGui
import os

class IviGuiInstrument(GuiWrapper,IviInstrument):
    """
    Instruments that offer the possibility to display a Graphical User Interface
    """
    
    def __init__(self):
        super(IviGuiInstrument, self).__init__()

    
    def gui(self):
        """opens a gui window"""

        window = super(IviGuiInstrument, self).gui()
        window.setWindowIcon(QtGui.QIcon(os.path.split(__file__)[0] \
                                         +"/icons/" + "iconeScope.gif"))
        window.setWindowTitle(self.logical_name)
        return window
    
    @classmethod 
    def menu_items(cls):
        """The objects of type MenuItem returned by this function allow the 
        PyInstrumentsConfigGui to know which menu items to add upon right click
        on an instrument that is handled by this class.
        """
        
        return [MenuItem("Graphical User Interface ...", cls.gui)] 