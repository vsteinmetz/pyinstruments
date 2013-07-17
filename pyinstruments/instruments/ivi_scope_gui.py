"""
class to add gui-capabilities to IVI-compliant spectrum analyzers
"""

from pyinstruments.instruments.gui_fetchable import GuiFetchable
from pyinstruments.wrappers import Wrapper
from pyinstruments.instruments.ivi_instrument import \
                                                IntermediateCollection
from pyinstruments.factories import use_for_ivi
from pyinstruments.instruments.iviguiinstruments import IviGuiInstrument

from guiwrappersutils import GuiWrapper
from numpy import array,linspace

@use_for_ivi("Scope")
class IviScopeGui(Wrapper, IviGuiInstrument):
    """
    class to add gui-capabilities to IVI-compliant spectrum analyzers
    """
    
    def __init__(self, *args, **kwds):
        super(IviScopeGui,self).__init__(*args,**kwds)
        IviGuiInstrument.__init__(self)
        self._wrap_attribute("Channels", \
                        IntermediateCollection(self.Channels, \
                        IviScopeGui.ChannelGui))
        
    def _setupUi(self, widget):
        """sets up the graphical user interface"""

        widget._setup_gui_element("Acquisition.RecordLength")
        widget._setup_gui_element("Acquisition.TimePerRecord")
        widget._setup_gui_element("Acquisition.StartTime")
        widget._setup_gui_element("Acquisition.Type", \
                                  normal = 0, \
                                  peakDetect = 1, \
                                  hiRes = 2, \
                                  enveloppe = 3, \
                                  average = 4)
        widget._setup_tabs_for_collection("Channels")

    class ChannelGui(Wrapper, GuiWrapper, GuiFetchable):
        """
        class to add gui-capabilities to the sub object Channel
        """
        
        def __init__(self, *args, **kwds):
            super(IviScopeGui.ChannelGui,self).__init__(*args,**kwds)
            GuiWrapper.__init__(self)
            GuiFetchable.__init__(self)
        
        def FetchXY(self):
            """returns an array with the X and Y columns filled.
            """
            
            (y_values, start, step) = self.FetchWaveform()
            n = len(y_values)
            return array([linspace(start, \
                                   start+step*n, \
                                   n, \
                                   endpoint = False), \
                          y_values])
        
        def _setupUi(self, widget):
            """sets up the graphical user interface"""
            
            widget._setup_gui_element("Enabled")
            widget._setup_gui_element("Coupling", \
                                      AC = 0, \
                                      DC = 1, \
                                      GND = 2)
            widget._setup_gui_element("InputFrequencyMax")
            widget._setup_gui_element("InputImpedance")
            widget._setup_gui_element("Offset")
            widget._setup_gui_element("Range")
            self._setup_fetch_utilities(widget)