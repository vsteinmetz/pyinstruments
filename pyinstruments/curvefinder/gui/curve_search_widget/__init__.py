from pyinstruments.curvefinder.gui.curve_search_widget.curve_filter_widgets import MultiFilterWidget
from pyinstruments.curvefinder.gui.curve_search_widget.list_curve_widget import ListCurveWidget
from pyinstruments.curvestore.models import CurveDB, model_monitor

from PyQt4 import QtCore, QtGui

class CurveSearchDockWidget(QtGui.QDockWidget):
    value_changed = QtCore.pyqtSignal()
    current_item_changed = QtCore.pyqtSignal(CurveDB)
    
    def __init__(self, parent=None):
        super(CurveSearchDockWidget, self).__init__(parent)
        self.widget = CurveSearchWidget()
        self.setWidget(self.widget)
        self.widget.value_changed.connect(self.value_changed)
        self.widget.current_item_changed.connect(self.current_item_changed)
        
    def select_by_id(self, id):
        self.widget.select_by_id(id)
        
    def refresh(self):
        self.widget.refresh()
        
class CurveSearchWidget(QtGui.QWidget):
    value_changed = QtCore.pyqtSignal()
    current_item_changed = QtCore.pyqtSignal(CurveDB)
    
    def __init__(self, parent=None):
        super(CurveSearchWidget, self).__init__(parent)
        self.curve_filter_widget = MultiFilterWidget()
        self.list_curve_widget = ListCurveWidget(self)
        self.lay = QtGui.QHBoxLayout()
        self.setLayout(self.lay)
        self.lay.addWidget(self.curve_filter_widget)
        self.lay.addWidget(self.list_curve_widget)
        self.curve_filter_widget.value_changed.connect(self.list_curve_widget.refresh)
        self.curve_filter_widget.value_changed.connect(self.value_changed)
        self.list_curve_widget.current_item_changed.connect(self.current_item_changed)
        model_monitor.fit_done.connect(self.refresh)
        
    def query(self):
        return self.curve_filter_widget.query()
    
    def select_by_id(self, id):
        return self.list_curve_widget.select_by_id(id)
    
    def refresh(self):
        self.list_curve_widget.refresh()