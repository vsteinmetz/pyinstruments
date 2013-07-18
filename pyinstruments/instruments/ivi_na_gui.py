"""
class to add gui-capabilities to IVI-compliant network analyzers
"""

from guiwrappersutils import GuiWrapper
from pyinstruments.instruments.gui_fetchable import GuiFetchable
from pyinstruments.wrappers import Wrapper
from pyinstruments.instruments.ivi_instrument import  IntermediateCollection
from pyinstruments.factories import use_for_ivi
from pyinstruments.instruments.iviguiinstruments import IviGuiInstrument
import mypandas
from hdnavigator import nav

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
            
            widget._setup_tabs_for_collection("Measurements")
    
        class GuiMeasurement(Wrapper, GuiWrapper, GuiFetchable):
            """wrapper for sub-sub-object Measurement
            """
            
            def __init__(self, *args, **kwds):
                super(IviNaGui.GuiChannel.GuiMeasurement, \
                                        self).__init__(*args, **kwds)
                GuiWrapper.__init__(self)
                GuiFetchable.__init__(self)

        
            def Create(self, out_port = None, in_port = None):
                """allows to create the measurement with default ports"""
                
                self._wrapped.Create(2, 1)
                
                for widget in self._widgets:
                    widget._gui_elements["Create"].setVisible(False)
                    widget._setup_gui_element("out_port")
                    widget._setup_gui_element("in_port")
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
                    
                    
            @property
            def in_port(self):
                in_port, out_port = self.GetSParameter()
                return in_port
            
            @in_port.setter
            def in_port(self, in_port):
                self._wrapped.Create(in_port, self.out_port)
            
            @property
            def out_port(self):
                in_port, out_port = self.GetSParameter()
                return out_port
            
            @out_port.setter
            def out_port(self, out_port):
                self._wrapped.Create(self.in_port, out_port)
            
            
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
                import mypandas
                x_y = self.FetchXYFormatted()
                mypandas.Series(x_y[1], index = x_y[0]).save(nav.next_file)
                nav.value_changed.emit()
                
            def save_curve_complex(self):
                """Saves the curve using the hdnavigator module to find the location"""
                import mypandas
                x_y = self.FetchXYComplex()
                mypandas.Series(x_y[1], index = x_y[0]).save(nav.next_file)
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
                widget._setup_gui_element("Create")
                widget._exit_layout()