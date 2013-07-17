"""
class to add gui-capabilities to IVI-compliant network analyzers
"""

from guiwrappersutils import GuiWrapper
from pyinstruments.instruments.gui_fetchable import GuiFetchable
from pyinstruments.wrappers import Wrapper
from pyinstruments.instruments.ivi_instrument import  IntermediateCollection
from pyinstruments.factories import use_for_ivi
from pyinstruments.instruments.iviguiinstruments import IviGuiInstrument
from numpy import array,linspace

@use_for_ivi("NA")
class IviNaGui(Wrapper, IviGuiInstrument):
    """
    class to add gui-capabilities to IVI-compliant network analyzers
    """
    
    def __init__(self, *args, **kwds):
        super(IviNaGui,self).__init__(*args,**kwds)
        GuiWrapper.__init__(self)
        self._wrap_attribute("Channels", \
                        IntermediateCollection(self.Channels, \
                        IviNaGui.GuiChannel))
    
    def _setupUi(self, widget):
        """sets up the graphical user interface"""
         
        widget._setup_tabs_for_collection("Channels")
    
    class GuiChannel(Wrapper, GuiWrapper):
        """wrapper for sub-object Channel"""
        
        def __init__(self, *args, **kwds):
            super(IviNaGui.GuiChannel, self).__init__(*args, **kwds)
            GuiWrapper.__init__(self)
            self._wrap_attribute("Measurements", \
                        IntermediateCollection(self.Measurements, \
                        IviNaGui.GuiChannel.GuiMeasurement))
            
        def _setupUi(self, widget):
            widget._setup_gui_element("Center")
            widget._setup_gui_element("Span")
            widget._setup_gui_element("Start")
            widget._setup_gui_element("Stop")
            widget._setup_gui_element("IFBandwidth")
            widget._setup_gui_element("Averaging")
            widget._setup_gui_element("AveragingFactor")
            
            widget._setup_tabs_for_collection( "Measurements")
    
        class GuiMeasurement(Wrapper, GuiWrapper, GuiFetchable):
            """wrapper for sub-sub-object Measurement
            """
            
            def __init__(self, *args, **kwds):
                super(IviNaGui.GuiChannel.GuiMeasurement, \
                                        self).__init__(*args, **kwds)
                GuiWrapper.__init__(self)
                GuiFetchable.__init__(self)
            
            def FetchXY(self):
                return array([self.FetchX(), self.FetchFormatted()])
            
            def _setupUi(self, widget):
                widget._setup_gui_element("AutoScale")
                self._setup_fetch_utilities(widget)
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    @property
    def Traces(self):
        return IntermediateCollection(self._wrapped.Traces, self.TraceGui)
    

    class TraceGui(Wrapper, GuiWrapper, GuiFetchable):
        """wrapper for sub-object Trace"""
    
        def __init__(self, *args, **kwds):
            super(IviSpecAnGui.TraceGui,self).__init__(*args,**kwds)
            GuiWrapper.__init__(self)
            GuiFetchable.__init__(self)
        
        def _setupUi(self, widget):
            """sets up the graphical user interface"""
            
            widget._setup_gui_element("DisplayEnabled")
            widget._setup_gui_element("UpdateEnabled")
            widget._setup_gui_element("Type", \
                                    ClearWrite = 1, \
                                    MaxHold = 2, \
                                    MinHold = 3, \
                                    Average = 4)
            widget._setup_gui_element("DetectorType", \
                                    Average = 1, \
                                    Pos = 2, \
                                    Neg = 3, \
                                    Samp = 4, \
                                    AverageAgain = 5, \
                                    Norm = 6, \
                                    Qpe = 7, \
                                    Eav = 8, \
                                    Rav = 0, \
                                    Off = 10)
            self._setup_fetch_utilities(widget)
            
        def FetchXY(self):
            """a custom function (not in the IVI driver) 
            that returns a numpy array with X and Y"""
            
            x = self.FetchX()
            y = self.FetchY()
            return array([x, y])
