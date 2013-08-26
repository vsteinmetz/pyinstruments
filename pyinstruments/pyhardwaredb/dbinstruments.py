from pyinstruments.pyhardware.instruments.gui_fetchable import GuiFetchable
from pyinstruments.pyhardware.instruments.ivi_scope_gui import IviScopeGui
from pyinstruments.pyhardware.instruments.ivi_spec_an_gui import IviSpecAnGui
from pyinstruments.pyhardware.instruments.ivi_na_gui import IviNaGui
from pyinstruments.pyhardware.instruments.ivi_instrument import \
                                                IntermediateCollection
from pyinstruments.curvefinder.qtgui.gui import CurveCreateWidget
from pyinstruments.curvefinder.models import Window, Tag, curve_db_from_curve
import json

from PyQt4 import QtCore, QtGui

 
class DBFetchable(object):
    def _get_initial_defaults(self):
        return {"default_name":'curve_%s'%self._type_str, \
         "default_window":'%s'%self._type_str, \
         "tags":["all"], \
         "comment":""}
        
    def get_curve(self):
        return curve_db_from_curve(super(DBFetchable, self).get_curve())
    
    def _get_defaults(self):
        settings = QtCore.QSettings("pyinstruments", "pyinstruments")
        kwds_str = str(settings.value("default_" + self._type_str).toString())
        if kwds_str != "":
            kwds = json.loads(kwds_str)
        else:
            kwds = self._get_initial_defaults()
        return kwds
    
    def _save_defaults(self, **kwds):
        settings = QtCore.QSettings("pyinstruments", "pyinstruments")
        settings.setValue("default_" + self._type_str, json.dumps(kwds))
    
    def _save_curve(self, curve):
        curve = curve_db_from_curve(curve)
        try:
            db_widget = self._dbwidget
        except AttributeError:
            pass
        else:
            curve.name = self._dbwidget.name
            curve.window_txt = self._dbwidget.window
            curve.save()
        
            tags = self._dbwidget.tags
            for tag_name in tags:
                (tag, new) = Tag.objects.get_or_create(name = tag_name)
                curve.tags.add(tag)
            curve.comment = self._dbwidget.comment
            
            self._save_defaults(default_name=curve.name, \
                                default_window=curve.window.name, \
                                comment=curve.comment, \
                                tags=tags)
        finally:
            curve.save()
    
    
    def _setup_fetch_utilities(self, widget):
        """sets up the gui to fetch the waveforms in widget"""
    
        self._dbwidget = CurveCreateWidget(**self._get_defaults())
        self._dbwidget.hide_save_button()
        p = self._dbwidget.palette()
        p.setColor(self._dbwidget.backgroundRole(), QtCore.Qt.gray)
        self._dbwidget.setPalette(p)
        self._dbwidget.setAutoFillBackground(True)
    
    
        widget.add_below(self._dbwidget)
        widget._setup_horizontal_layout()
        self._add_fetch_buttons(widget)
        widget._exit_layout()

class TraceGuiDB(DBFetchable, IviSpecAnGui.TraceGui):
    _type_str = 'specan'

class ChannelGuiDB(DBFetchable, IviScopeGui.ChannelGui):
    _type_str = 'scope'
        
class MeasurementGuiDB(DBFetchable, IviNaGui.ChannelGui.MeasurementGui):
    _type_str = 'na'
        
    def get_curve_complex(self):
        return curve_db_from_curve( \
                    super(MeasurementGuiDB, self).get_curve_complex())
        
    def get_curve_formatted(self):
        return curve_db_from_curve( \
                    super(MeasurementGuiDB, self).get_curve_formatted())
        
        
        
        
IviSpecAnGui.TraceGui = TraceGuiDB
IviScopeGui.ChannelGui = ChannelGuiDB
IviNaGui.ChannelGui.MeasurementGui = MeasurementGuiDB