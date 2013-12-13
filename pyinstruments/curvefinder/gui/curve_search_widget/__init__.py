from pyinstruments.curvefinder.gui.curve_search_widget.curve_filter_widgets import MultiFilterWidget
from pyinstruments.curvefinder.gui.curve_search_widget.list_curve_widget import ListCurveWidget
from pyinstruments.curvestore.models import CurveDB, model_monitor

from PyQt4 import QtCore, QtGui

class CurveSearchDockWidget(QtGui.QDockWidget):
    value_changed = QtCore.pyqtSignal()
    current_item_changed = QtCore.pyqtSignal(CurveDB)
    refresh_clicked = QtCore.pyqtSignal()
    
    def __init__(self, parent=None):
        super(CurveSearchDockWidget, self).__init__(parent)
        self.widget = CurveSearchWidget()
        self.setWidget(self.widget)
        self.widget.value_changed.connect(self.value_changed)
        self.widget.current_item_changed.connect(self.current_item_changed)
        self.widget.refresh_clicked.connect(self.refresh_clicked)
        
    def select_by_id(self, id):
        self.widget.select_by_id(id)
        
    def refresh(self):
        self.widget.refresh()
        
    def refresh_one_id(self, id):
        self.widget.refresh_one_id(id)
        
class CurveSearchWidget(QtGui.QWidget):
    value_changed = QtCore.pyqtSignal()
    current_item_changed = QtCore.pyqtSignal(CurveDB)
    refresh_clicked = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super(CurveSearchWidget, self).__init__(parent)
        self.curve_filter_widget = MultiFilterWidget()
        self.list_curve_widget = ListCurveWidget(self)
        self.lay = QtGui.QHBoxLayout()
        self.setLayout(self.lay)
        self.lay.addWidget(self.curve_filter_widget)
        self.lay.addWidget(self.list_curve_widget)
        #self.curve_filter_widget.value_changed.connect(self.list_curve_widget.refresh)
        self.curve_filter_widget.value_changed.connect(self.value_changed)
        self.list_curve_widget.current_item_changed.connect(self.current_item_changed)
        self.list_curve_widget.refresh_clicked.connect(self.refresh_clicked)
        model_monitor.child_added.connect(self.refresh_one_id)
        
    def query(self):
        return self.curve_filter_widget.query()
    
    def query_string(self):
        return self.curve_filter_widget.query_string()
    
    def select_by_id(self, id):
        return self.list_curve_widget.select_by_id(id)
    
    def refresh(self):
        self.list_curve_widget.refresh()
    
    def refresh_one_id(self, id):
        self.list_curve_widget.refresh_one_id(id)