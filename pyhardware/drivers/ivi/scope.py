from pyhardware.drivers.ivi import IviDriver, \
                                                 add_fields
from pyhardware.utils.guiwrappersutils import GuiWrapper
from pyhardware.utils.gui_fetch_utils import FetcherMixin
from curve import Curve

from pyivi.ivicom.iviscope import ShortCutScope
from PyQt4 import QtCore, QtGui
import pandas

                
class IviScopeDriver(IviDriver, GuiWrapper, FetcherMixin):
    specialized_name = 'IviScope'
    _fields = []
    def __init__(self, logical_name, pyividriver):
        super(IviScopeDriver, self).__init__(logical_name, pyividriver)
        GuiWrapper.__init__(self)
        self.channel_idxs = self.driver.sc.channel_idxs
    
    def _setupUi(self, widget):
        """sets up the graphical user interface"""
        
        widget._setup_vertical_layout()
        widget._setup_horizontal_layout()
        widget._setup_vertical_layout()
        for field in self._fields:
            if field=='channel_idx':
                widget._exit_layout()
                widget._setup_vertical_layout()
            choices = None
            if hasattr(self, field + 's'):
                choices = self.__getattribute__(field + 's')
            widget._setup_gui_element(field, choices)
        widget._exit_layout()
        widget._exit_layout()
        self._setup_fetch_buttons(widget)
    
    def _get_curve(self):
        x_y = self.driver.sc.fetch()
        meta = dict()
        
        meta["name"] = "scope_curve"
        meta["acquisition_type"] = self.acquisition_types[self.acquisition_type]
        meta["averaging"] = self.number_of_averages
        meta["start_time"] = self.start_time
        meta["record_length"] = self.record_length
        meta["sample_rate"] = self.sample_rate
        meta["coupling"] = self.ch_couplings[self.ch_coupling]
        meta["full_range"] = self.ch_range
        meta["offset"] = self.ch_offset
        meta["input_freq_max"] = self.ch_input_frequency_max
        meta["input_impedance"] = self.ch_input_impedance
        meta["channel"] = self.channel_idxs[self.channel_idx]
        meta["curve_type"] = "ScopeCurve"
        meta["instrument_logical_name"] = self.logical_name
        
        curve = Curve()
        curve.set_data(pandas.Series(x_y[1], index = x_y[0]))
        curve.set_params(**meta)
        return curve

add_fields(IviScopeDriver, ShortCutScope._fields)
add_fields(IviScopeDriver, ['channel_idx'])
add_fields(IviScopeDriver, ShortCutScope._ch_fields)
add_fields(IviScopeDriver, ["sample_modes",
                            "acquisition_types",
                            "ch_couplings"], add_ref=False)
