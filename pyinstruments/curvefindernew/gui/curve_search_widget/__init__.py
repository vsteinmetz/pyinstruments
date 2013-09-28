from pyinstruments.curvefindernew.gui.curve_search_widget.curve_filter_widgets import MultiFilterWidget
from pyinstruments.curvefindernew.gui.curve_search_widget.list_curve_widget import ListCurveWidget

from PyQt4 import QtCore, QtGui

class CurveSearchDockWidget(QtGui.QDockWidget):
    def __init__(self, parent=None):
        super(CurveSearchDockWidget, self).__init__(parent)
        self.widget = CurveSearchWidget()
        self.setWidget(self.widget)

class CurveSearchWidget(QtGui.QWidget):
    def __init__(self, parent=None):
        super(CurveSearchWidget, self).__init__(parent)
        self.curve_filter_widget = MultiFilterWidget()
        self.list_curve_widget = ListCurveWidget(self)
        self.lay = QtGui.QHBoxLayout()
        self.setLayout(self.lay)
        self.lay.addWidget(self.curve_filter_widget)
        self.lay.addWidget(self.list_curve_widget)
        self.curve_filter_widget.value_changed.connect(self.list_curve_widget.refresh)
        
    def query(self):
        return self.curve_filter_widget.query()