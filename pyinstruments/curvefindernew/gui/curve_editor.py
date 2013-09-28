from PyQt4 import QtGui, QtCore
from pyinstruments.curvefinder.qtgui.curvesearch_widget import DateConstraintWidget, \
                                      StringFilterWidget, \
                                      ComboFilterWidget, \
                                      TagFilterWidget, \
                                      BoolFilterWidget
from pyinstruments.curvefinder.models import Window, CurveDB
from pyinstruments.curvefinder.qtgui.gui import CurveCreateWidget
from curve_editor_menus import CurveEditorMenuBar, CurveEditorToolBar, NamedCheckBox 
import pyinstruments.datastore.settings
from pyinstruments.curvefinder.qtgui.plot_window import PlotDialog
from pyinstruments.curvefinder.fitting import FitFunctions

from numpy import array
from guiqwt import plot
from guiqwt.builder import make
import datetime
import dateutil
import json
from collections import OrderedDict
import os
import functools



WINDOWS = dict()

def get_window(name):
    try:
        win = WINDOWS[name]
    except KeyError:
        win = PlotDialog(name)
        WINDOWS[name] = win
    return win

class CurveEditor(QtGui.QMainWindow, object):
        
    def __init__(self):
        super(CurveEditor, self).__init__()
        
        self.menubar = CurveEditorMenuBar(self)
            
        self.setMenuBar(self.menubar)
        self.search_widget = CurveSearchWidget(self)
        self.addDockWidget(\
                QtCore.Qt.DockWidgetArea(QtCore.Qt.LeftDockWidgetArea), \
                self.search_widget)
        self.toolbar = CurveEditorToolBar(self)
        
        self.addToolBar(self.toolbar)
        self.toolbar.popup_unread_activated.connect(\
                                            self.activate_popup_unread)
        self.toolbar.popup_unread_deactivated.connect(\
                                            self.deactivate_popup_unread)
        
        self.curve_display_widget = CurveDisplayWidget(self)
        self.setCentralWidget(self._curve_display_widget)
        self.search_widget.value_changed.connect(self.refresh)
        self.search_widget.value_changed.connect(self.save_defaults)        
        self.search_widget.current_item_changed.connect(self.display)
        
        
        settings = QtCore.QSettings("pyinstruments", "pyinstruments")
        default_json = str(settings.value("curve_editor_defaults").\
                                                            toString())
        if default_json != "":
            defaults = json.loads(default_json)
            for key in ["date_lte", "date_gte", "date_equals"]:
                enabled, val = defaults[key]
                if val:
                    defaults[key] = enabled, dateutil.parser.parse(val)
        else:
            defaults = {}
        self.set_defaults(**defaults)
        
        self.popup_timer = QtCore.QTimer()
        self.popup_timer.timeout.connect(self.popup_unread_curves)
        self.popup_timer.setSingleShot(False)
        self.popup_timer.setInterval(500) #ms
        self.popup_unread = False
        
        self.show()

    @property
    def plot_popups(self):
        return self.toolbar._checkbox_plot_popups.check_state

    def popup_unread_curves(self):
        unread = CurveDB.objects.filter(user_has_read=False)
        if unread:
            self.search_widget.refresh()
            curve = unread[0]
            self.display(curve)
            if self.plot_popups:
                win = get_window(curve.window_txt)
                win.plot(curve)
                

    def activate_popup_unread(self):
        self.popup_unread = True
        self.popup_timer.start()
    
    def deactivate_popup_unread(self):
        self.popup_unread = False
        self.popup_timer.stop()
    
    def display(self, curve):
        self._curve_display_widget.display(curve)
        if  curve:
            self.search_widget.select_by_id(curve.id)
    
    def set_defaults(self, **kwds):
        self.search_widget.set_defaults(**kwds)
    
    def save_defaults(self):
        defaults = self.search_widget.get_values()
        for key in ["date_lte", "date_gte", "date_equals"]:
            enabled, val = defaults[key]
            val = str(val)
            defaults[key] = enabled, val
        defaults_json = json.dumps(defaults)
        settings = QtCore.QSettings("pyinstruments", "pyinstruments")
        settings.setValue("curve_editor_defaults", defaults_json)
    
    def refresh(self):
        self.search_widget.refresh()
    
    def getsearch_widget(self):
        """
        mostly for interactive debugging purposes
        """
        
        return self.search_widget._widget_full
    
    def get_list_widget(self):
        """
        mostly for interactive debugging purposes
        """
        
        return self.search_widget._widget_full._list_widget
    
    def get_curve_display_widget(self):
        """
        mostly for interactive debugging purposes
        """
        
        return self._curve_display_widget
    
    #def _get_list_curve_widget(self):
    #    return ListCurveWidget(self)
        
    def get_query_set(self):
        return self.search_widget.get_query_set()
        

