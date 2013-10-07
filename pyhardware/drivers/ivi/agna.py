from pyhardware.drivers.ivi import IviDriver, \
                                                 add_fields
from pyhardware.utils.guiwrappersutils import GuiWrapper
from pyhardware.utils.gui_fetch_utils import FetcherMixin
from curve import Curve

from pyivi.ivicom.agna import ShortCutNA
from PyQt4 import QtCore, QtGui
import pandas


class IviAgNADriver(IviDriver, GuiWrapper, FetcherMixin):
    specialized_name = ''
    _fields = []
    
    def __init__(self, logical_name, pyividriver):
        super(IviAgNADriver, self).__init__(logical_name, pyividriver)
        GuiWrapper.__init__(self)
        self.channel_idxs = self.driver.sc.channel_idxs
        self.measurement_idxs = self.driver.sc.measurement_idxs
    
    def _setupUi(self, widget):
        """sets up the graphical user interface"""
        
        widget._setup_vertical_layout()
        widget._setup_horizontal_layout()
        widget._setup_vertical_layout()
        for field in self._fields:
            if field=='frequency_center':
                widget._exit_layout()
                widget._setup_vertical_layout()
                continue
            choices = None
            if hasattr(self, field + 's'):
                choices = self.__getattribute__(field + 's')
            widget._setup_gui_element(field, choices)
        widget._exit_layout()
        widget._exit_layout()
        self._setup_fetch_buttons(widget)
        
#get the curve automatically in a complex format in linear scale
    def _get_curve(self):
        x_y = self.driver.sc.fetch("complex")
        meta = dict()
        
        meta["name"] = "na_curve"
        meta["curve_type"] = "NaCurveComplex"
        meta["averaging"] = self.averaging_factor*self.averaging
        meta["center_freq"] = self.frequency_center
        meta["start_freq"] = self.frequency_start
        meta["stop_freq"] = self.frequency_stop
        meta["span"] = self.span
        meta["bandwidth"] = self.if_bandwidth
        meta["sweep_time"] = self.sweep_time
        meta["output_port"] = self.output_port
        meta["input_port"] = self.input_port

        meta["format"] = self.formats[self.format]
        
        meta["measurement"] = self.measurement_idxs[self.measurement_idx]
        meta["channel"] = self.channel_idxs[self.channel_idx]
        meta["instrument_type"] = "NA"
        meta["instrument_logical_name"] = self.logical_name 
        
        curve = Curve()
        curve.set_data(pandas.Series(x_y[1], index = x_y[0]))
        curve.set_params(**meta)
        return curve

#get the curve shown on the display
    def _get_curve_disp(self):
        x_y = self.driver.sc.fetch()
        meta = dict()
        
        
        meta["name"] = "na_curve"
        meta["curve_type"] = "NaCurve"
        meta["averaging"] = self.averaging_factor*self.averaging
        meta["center_freq"] = self.frequency_center
        meta["start_freq"] = self.frequency_start
        meta["stop_freq"] = self.frequency_stop
        meta["span"] = self.span
        meta["bandwidth"] = self.if_bandwidth
        meta["sweep_time"] = self.sweep_time
        meta["output_port"] = self.output_port
        meta["input_port"] = self.input_port

        meta["format"] = self.formats[self.format]
        
        meta["measurement"] = self.measurement_idxs[self.measurement_idx]
        meta["channel"] = self.channel_idxs[self.channel_idx]
        meta["instrument_type"] = "NA"
        meta["instrument_logical_name"] = self.logical_name 
        
        curve = Curve()
        curve.set_data(pandas.Series(x_y[1], index = x_y[0]))
        curve.set_params(**meta)
        return curve

    @classmethod
    def supported_software_modules(cls):
        return ['AgNA']
    
add_fields(IviAgNADriver, ShortCutNA._fields)
add_fields(IviAgNADriver, ['channel_idx'])
add_fields(IviAgNADriver, ShortCutNA._ch_fields)
add_fields(IviAgNADriver, ['measurement_idx'])
add_fields(IviAgNADriver, ShortCutNA._m_fields)
add_fields(IviAgNADriver, ["sweep_types",
                           "formats"], add_ref=False)
    