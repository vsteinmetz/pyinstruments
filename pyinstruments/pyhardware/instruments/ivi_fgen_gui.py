"""
class to add gui-capabilities to IVI-compliant spectrum analyzers
"""

from pyinstruments.pyhardware.instruments.gui_fetchable import GuiFetchable
from pyinstruments.pyhardware.wrappers import Wrapper
from pyinstruments.pyhardware.instruments.ivi_instrument import \
                                                IntermediateCollection
from pyinstruments.pyhardware.factories import use_for_ivi
from pyinstruments.pyhardware.instruments.iviguiinstruments import IviGuiInstrument

from pyinstruments.utils.guiwrappersutils import GuiWrapper
from numpy import array,linspace

@use_for_ivi("IviFgen")
class IviFgenGui(Wrapper, IviGuiInstrument):
    """
    class to add gui-capabilities to IVI-compliant function generators
    """
    
    def __init__(self, *args, **kwds):
        super(IviFgenGui,self).__init__(*args,**kwds)
        IviGuiInstrument.__init__(self)
         
    def _setupUi(self, widget):
        """sets up the graphical user interface"""
        widget._setup_horizontal_layout()
        widget._setup_gui_element("Acquisition.Start")
        widget._setup_gui_element("Acquisition.Stop")
        widget._exit_layout()
        pass


    @property
    def Offset(self):
        return self.get_Offset()
    
    @Offset.setter
    def Offset(self, val):
        return self.set_Offset(val)