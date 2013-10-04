from pyhardware.drivers.ivi import IviDriver, \
                                                 add_fields
from pyhardware.utils.guiwrappersutils import GuiWrapper
from pyhardware.utils.gui_fetch_utils import FetcherMixin
from curve import Curve

from pyivi.ivicom.ivispecan import ShortCutSpecAn
import pandas


                
class IviSpecAnDriver(IviDriver, GuiWrapper, FetcherMixin):
    specialized_name = 'IviSpecAn'
    _fields = []
    def __init__(self, logical_name, pyividriver):
        super(IviSpecAnDriver, self).__init__(logical_name, pyividriver)
        GuiWrapper.__init__(self)
        self.trace_idxs = self.driver.sc.trace_idxs
    
    def _setupUi(self, widget):
        """sets up the graphical user interface"""
        
        widget._setup_vertical_layout()
        widget._setup_horizontal_layout()
        widget._setup_vertical_layout()
        for field in self._fields:
            if field == 'trace_idx':
                widget._exit_layout()
                widget._setup_vertical_layout()
            choices = None
            if hasattr(self.driver.sc, field + 's'):
                choices = self.driver.sc.__getattribute__(field + 's')
            widget._setup_gui_element(field, choices)
        widget._exit_layout()
        widget._exit_layout()
        self._setup_fetch_buttons(widget)
    
            
    def _get_curve(self):
            x_y = self.driver.sc.fetch()
            meta = dict()
            
            meta["name"] = "specan_curve"
            
            meta["curve_type"] = 'SpecAnCurve'
            meta["trace_type"] = self.tr_types[self.tr_type]
            meta["averaging"] = self.number_of_sweeps
            meta["center_freq"] = self.frequency_center
            meta["start_freq"] = self.frequency_start
            meta["stop_freq"] = self.frequency_stop
            meta["span"] = self.span
            meta["bandwidth"] = self.resolution_bandwidth
            meta["sweep_time"] = self.sweep_time
            
            meta["detector_type"] = self.detector_types[self.detector_type]
            meta["trace"] = self.trace_idxs[self.trace_idx]
            meta["instrument_type"] = "SpecAn"
            meta["instrument_logical_name"] = self.logical_name
            
            curve = Curve(pandas.Series(x_y[1], index = x_y[0]), meta = meta)
            return curve
        
add_fields(IviSpecAnDriver, ShortCutSpecAn._fields)
add_fields(IviSpecAnDriver, ['trace_idx'])
add_fields(IviSpecAnDriver, ShortCutSpecAn._tr_fields)
add_fields(IviSpecAnDriver, ["detector_types",
                            "tr_types"], add_ref=False)
#add_fields(IviScopeDriver, [field[0] for field in ShortCutScope._channel_related_fields])
    