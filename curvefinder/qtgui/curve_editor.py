from PyQt4 import QtGui, QtCore
from curvefinder.qtgui.curve_filter_widget import DateConstraintWidget, \
                                      StringFilterWidget, \
                                      ComboFilterWidget
from curvefinder.models import Window, CurveDB

class CurveEditor(QtGui.QMainWindow):
    def __init__(self):
        super(CurveEditor, self).__init__()
        self._filter_widget = self._get_filter_widget()
        self._list_curve_widget = self._get_list_curve_widget()
        self.addDockWidget(\
                QtCore.Qt.DockWidgetArea(QtCore.Qt.RightDockWidgetArea), \
                self._filter_widget)
        self.addDockWidget(\
                QtCore.Qt.DockWidgetArea(QtCore.Qt.LeftDockWidgetArea), \
                self._list_curve_widget)
        self._curve_display_widget = self._get_curve_display_widget()
        self.setCentralWidget(self._curve_display_widget)
        self._filter_widget.value_changed.connect(self.refresh)
        self.show()
        
    def refresh(self):
        print "refresh"
        self._list_curve_widget.refresh()    
    
    def _get_filter_widget(self):
        return FilterWidgetFull(self)
    
    def _get_curve_display_widget(self):
        return CurveDisplayWidget(self)
    
    def _get_list_curve_widget(self):
        return ListCurveWidget(self)
        
    def get_query_set(self):
        return self._filter_widget.get_query_set()
        
    
class FilterWidgetFull(QtGui.QDockWidget):
    def __init__(self, parent):
        super(FilterWidgetFull, self).__init__(parent)
        self._widget_full = self._get_filter_widget()
        self._widget_full.value_changed.connect(self.value_changed)
        self.setWidget(self._widget_full)
    
    value_changed = QtCore.pyqtSignal(name = "value_changed")
    
    def get_query_set(self):
        return self._widget_full.get_query_set()
    
    def _get_filter_widget(self):
        class InnerFilterWidgetFull(QtGui.QWidget):
            def __init__(self, parent):
                super(InnerFilterWidgetFull, self).__init__(parent)
                self._filter_layout = QtGui.QVBoxLayout()
                self._filters = []
                self._filters.append(DateConstraintWidget('=', self))
                self._filters.append(DateConstraintWidget('>=', self))
                self._filters.append(DateConstraintWidget('<=', self))
                self._filters.append(StringFilterWidget('name', self))
                self._filters.append(StringFilterWidget('comment', self))
                self._filters.append(ComboFilterWidget(Window, 'window', self))    
                
            
                for filter in self._filters:
                    self._filter_layout.addWidget(filter)
                    filter.value_changed.connect(self.value_changed)
                self.setLayout(self._filter_layout)
                
            value_changed = QtCore.pyqtSignal(name = "value_changed")
                
            def get_query_set(self):
                kwds = dict()
                for filter in self._filters:
                    kwds.update(filter.get_kwds_for_query())
                return CurveDB.objects.filter(**kwds)
            
        return InnerFilterWidgetFull(self)
        
        
class ListCurveWidget(QtGui.QDockWidget):
    def __init__(self, parent):
        super(ListCurveWidget, self).__init__(parent)
        self._tree_widget = self._get_tree_widget()
        self.setWidget(self._tree_widget)
        self.refresh()
        
    def refresh(self):
        curves = self.parent().get_query_set()
        self._tree_widget.clear()
        for curve in curves:
            self._tree_widget.addTopLevelItem(QtGui.QTreeWidgetItem( \
                                                            [curve.name]))
    
    def _get_tree_widget(self):
        class ListTreeWidget(QtGui.QTreeWidget):
            def __init__(self, parent):
                super(ListTreeWidget, self).__init__(parent)                    
                self.headerItem().setText(0, "curve name")
        return ListTreeWidget(self)

class CurveDisplayWidget(QtGui.QWidget):
    pass