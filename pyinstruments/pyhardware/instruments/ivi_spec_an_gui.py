"""
class to add gui-capabilities to IVI-compliant spectrum analyzers
"""

from pyinstruments.pyhardware.instruments import choices
from pyinstruments.utils.guiwrappersutils import GuiWrapper
from pyinstruments.pyhardware.instruments.gui_fetchable import GuiFetchable
from pyinstruments.pyhardware.wrappers import Wrapper
from pyinstruments.pyhardware.instruments.ivi_instrument import  IntermediateCollection
from pyinstruments.pyhardware.factories import use_for_ivi
from pyinstruments.pyhardware.instruments.iviguiinstruments import IviGuiInstrument

from numpy import array,linspace
from pyinstruments.utils.curve import Curve
import pandas

@use_for_ivi("IviSpecAn")
class IviSpecAnGui(Wrapper, IviGuiInstrument):
    """
    class to add gui-capabilities to IVI-compliant spectrum analyzers
    """
    
    def __init__(self, *args, **kwds):
        super(IviSpecAnGui,self).__init__(*args,**kwds)
        IviGuiInstrument.__init__(self)
        self._wrap_attribute("Traces", \
                        IntermediateCollection(self.Traces, \
                        IviSpecAnGui.TraceGui))
    
    def _setupUi(self, widget):
        """sets up the graphical user interface"""
        

        widget._setup_horizontal_layout()
        widget._setup_gui_element("CenterFrequency")
        widget._setup_gui_element("Span")
        widget._exit_layout()  
        widget._setup_horizontal_layout()                
        widget._setup_gui_element("Start")
        widget._setup_gui_element("Stop")
        widget._exit_layout()  
        widget._setup_horizontal_layout()                  
        widget._setup_gui_element("ResolutionBandwidth")
        widget._setup_gui_element("Average.NumberOfSweeps")
        widget._exit_layout() 
        widget._setup_tabs_for_collection("Traces")


    class TraceGui(Wrapper, GuiWrapper, GuiFetchable):
        """wrapper for sub-object Trace"""
    
        def __init__(self, *args, **kwds):
            Wrapper.__init__(self, *args,**kwds)
            GuiWrapper.__init__(self)
            GuiFetchable.__init__(self)
        
        def _setupUi(self, widget):
            """sets up the graphical user interface"""
            
            widget._setup_horizontal_layout()  
            widget._setup_gui_element("DisplayEnabled")
            widget._setup_gui_element("UpdateEnabled")
            widget._exit_layout()             
            widget._setup_horizontal_layout()  
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
            widget._exit_layout() 
            self._setup_fetch_utilities(widget)
        
        acquisition_types = choices.spec_an_acquisition_types
        detector_types = choices.spec_an_detector_types
        
        def get_curve(self):
            x_y = self.FetchXY()
            meta = dict()
            
            meta["curve_type"] = 'SpecAnCurve'
            meta["acquisition_type"] = self.acquisition_types[self.Type][0]
            meta["averaging"] = self.wrapper_parent.Average.NumberOfSweeps
            meta["center_freq"] = self.wrapper_parent.CenterFrequency
            meta["start_freq"] = self.wrapper_parent.Start
            meta["stop_freq"] = self.wrapper_parent.Stop
            meta["span"] = self.wrapper_parent.Span
            meta["bandwidth"] = self.wrapper_parent.ResolutionBandwidth
            
            meta["detector_type"] = self.detector_types[self.DetectorType][0]
            meta["trace"] = self.wrapper_name
            meta["instrument_type"] = "SpecAn"
            meta["instrument_logical_name"] = \
                                self.wrapper_parent.logical_name
            
            curve = Curve(pandas.Series(x_y[1], index = x_y[0]), meta = meta)
            return curve
            
        def FetchXY(self):
            """a custom function (not in the IVI driver) 
            that returns a numpy array with X and Y"""
            
            x = self.FetchX()
            y = self.FetchY()
            return array([x, y])


