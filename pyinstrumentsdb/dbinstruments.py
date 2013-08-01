from pyinstruments import use_for_ivi
from pyinstruments.instruments.ivi_scope_gui import IviScopeGui
from pyinstruments.instruments.ivi_spec_an_gui import IviSpecAnGui
from pyinstruments.instruments.ivi_na_gui import IviNaGui
from pyinstruments.instruments.ivi_instrument import \
                                                IntermediateCollection
from curvefinder.qtgui.gui import CurveCreateWidget
from curvefinder.loadsave import save

from PyQt4 import QtCore, QtGui





def _save_curve_with_db(self):
    """Saves the curve using the dbwidget's values"""

    curve = self.get_curve()
    save(curve, \
         self._dbwidget.name, \
         self._dbwidget.window, \
         self._dbwidget.tags, \
         self._dbwidget.comment)

def _setup_fetch_utilities_with_db_widget(self, widget):
    """sets up the gui to fetch the waveforms in widget"""

    p = self._dbwidget.palette()
    p.setColor(self._dbwidget.backgroundRole(), QtCore.Qt.gray)
    self._dbwidget.setPalette(p)
    self._dbwidget.setAutoFillBackground(True)


    widget.add_below(self._dbwidget)
    widget._setup_horizontal_layout()
    widget._setup_gui_element("plot_xy")
    widget._setup_gui_element("xy_to_clipboard")
    widget._setup_gui_element("save_curve")
    widget._exit_layout()

def _setup_fetch_utilities_with_db_widget_for_na(self, widget):
    self._dbwidget = CurveCreateWidget(\
                                        default_name = "na_curve", \
                                        default_window = "na")
    p = self._dbwidget.palette()
    p.setColor(self._dbwidget.backgroundRole(), QtCore.Qt.gray)
    self._dbwidget.setPalette(p)
    self._dbwidget.setAutoFillBackground(True)
    widget.add_below(self._dbwidget)

    
def _save_curve_formatted_with_db(self):
    curve = self.get_curve_formatted()
    save(curve, \
         self._dbwidget.name, \
         self._dbwidget.window, \
         self._dbwidget.tags, \
         self._dbwidget.comment)
    
def _save_curve_complex_with_db(self):
    curve = self.get_curve_complex()
    save(curve, \
         self._dbwidget.name, \
         self._dbwidget.window, \
         self._dbwidget.tags, \
         self._dbwidget.comment)

IviNaGui.GuiChannel.GuiMeasurement._setup_fetch_utilities = \
            _setup_fetch_utilities_with_db_widget_for_na
IviNaGui.GuiChannel.GuiMeasurement.save_curve_formatted = \
            _save_curve_formatted_with_db
IviNaGui.GuiChannel.GuiMeasurement.save_curve_complex = \
            _save_curve_complex_with_db

@use_for_ivi("IviScope")
class IviScopeGuiDB(IviScopeGui):
    
    def __init__(self, *args, **kwds):
        super(IviScopeGuiDB, self).__init__(*args, **kwds)
        self._wrap_attribute("Channels", \
                        IntermediateCollection(self.Channels, \
                        IviScopeGuiDB.ChannelGuiDB))
        
        
    class ChannelGuiDB(IviScopeGui.ChannelGui):
        def __init__(self, *args, **kwds):
            IviScopeGui.ChannelGui.__init__(self,*args, **kwds)
            self._dbwidget = CurveCreateWidget(default_name = "scope_curve", \
                                           default_window = "scope")
        
        _setup_fetch_utilities = _setup_fetch_utilities_with_db_widget
        save_curve = _save_curve_with_db
            
            
@use_for_ivi("IviSpecAn")
class IviSpecAnGuiDB(IviSpecAnGui):
    
    def __init__(self, *args, **kwds):
        super(IviSpecAnGuiDB, self).__init__(*args, **kwds)
        self._wrap_attribute("Traces", \
                        IntermediateCollection(self.Traces, \
                        IviSpecAnGuiDB.TraceGuiDB))
        
    class TraceGuiDB(IviSpecAnGui.TraceGui):
        _setup_fetch_utilities = _setup_fetch_utilities_with_db_widget
        save_curve = _save_curve_with_db
        
        def __init__(self, *args, **kwds):
            IviSpecAnGui.TraceGui.__init__(self, *args, **kwds)
            self._dbwidget = CurveCreateWidget(default_name = "spec_an_curve", \
                                           default_window = "spec_an")
            

