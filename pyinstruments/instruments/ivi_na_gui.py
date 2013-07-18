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
import mypandas

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
                self.out_port = 2
                self.in_port = 1

        
            def Create(self, out_port = None, in_port = None):
                """allows to create the measurement with default ports"""
                
                if out_port == None:
                    out_port = self.out_port
                if in_port == None:
                    in_port = self.in_port    
                self._wrapped.Create(out_port, in_port)
                
                for widget in self._widgets:
                    widget._setup_horizontal_layout()
                    widget._setup_gui_element("Format", \
                                          LogMag = 0, \
                                          LinMag = 1, \
                                          Phase = 2, \
                                          GroupDelay = 3, \
                                          SWR = 4, \
                                          Real = 5, \
                                          Imag = 6, \
                                          Polar = 7, \
                                          Smith = 8, \
                                          SLinear = 9, \
                                          SLogarithmic = 10, \
                                          SComplex = 11, \
                                          SAdmittance = 12, \
                                          PLinear = 13, \
                                          PLogarithmic = 14, \
                                          UPhase = 15, \
                                          PPhase = 16)
                    widget._setup_gui_element("AutoScale")
                    widget._exit_layout()
                    self._setup_hdnavigator_widget(widget)

                    widget._setup_horizontal_layout()
                    widget._setup_gui_element("plot_xy_formatted")
                    widget._setup_gui_element("xy_formatted_to_clipboard")
                    widget._setup_gui_element("save_curve_formatted")
                    widget._exit_layout()
                    
                    widget._setup_horizontal_layout()
                    widget._setup_gui_element("plot_xy_square_mod")
                    widget._setup_gui_element("xy_complex_to_clipboard")
                    widget._setup_gui_element("save_curve_complex")
                    widget._exit_layout()
                    
                    
                
            def FetchXY(self):
                return array([self.FetchX(), self.FetchFormatted()])
            
            def FetchXYFormatted(self):
                return array([self.FetchX(), self.FetchFormatted()])
            
            def FetchXYComplex(self):
                return array([self.FetchX(), self.FetchComplex()])
            
            def plot_xy_formatted(self):
                """uses pylab to plot X and Y"""
                import pylab
                data = self.FetchXYFormatted()
                pylab.plot(data[0], data[1])
                pylab.show()
                                    
            def plot_xy_square_mod(self):
                """uses pylab to plot X and Y"""
                import pylab
                data = self.FetchXYComplex()
                pylab.plot(data[0], abs(data[1])**2)
                pylab.show()
                                                            
            
            def save_curve_formatted(self):
                """Saves the curve using the hdnavigator module to find the location"""
                import myPandas
                x_y = self.FetchXYFormatted()
                myPandas.Series(x_y[1], index = x_y[0]).save(nav.next_file)
                nav.value_changed.emit()
                
            def save_curve_complex(self):
                """Saves the curve using the hdnavigator module to find the location"""
                import myPandas
                x_y = self.FetchXYComplex()
                myPandas.Series(x_y[1], index = x_y[0]).save(nav.next_file)
                nav.value_changed.emit()
            
            def xy_formatted_to_clipboard(self):
                """copies X Y columnwise in the clipboard"""
                data = self.FetchXYFormatted()
                import StringIO
                string = StringIO.StringIO()
                fmt = "%.9g"
                numpy.savetxt(string, data.transpose(), delimiter = "\t", fmt = fmt)
                
                from pyinstruments import _APP
                clip = _APP.clipboard()
                clip.setText(string.getvalue())
                
            def xy_complex_to_clipboard(self):
                """copies X Y columnwise in the clipboard"""
                data = self.FetchXYComplex()
                import StringIO
                string = StringIO.StringIO()
                fmt = "%.9g"
                numpy.savetxt(string, data.transpose(), delimiter = "\t", fmt = fmt)
                
                from pyinstruments import _APP
                clip = _APP.clipboard()
                clip.setText(string.getvalue())
            
            
            def _setupUi(self, widget):
                widget._setup_horizontal_layout()
                widget._setup_gui_element("out_port")
                widget._setup_gui_element("in_port")
                widget._setup_gui_element("Create")
                widget._exit_layout()
                
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
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
