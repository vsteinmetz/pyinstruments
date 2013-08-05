from PyQt4 import QtGui, QtCore
from curvefinder.qtgui.curve_filter_widget import DateConstraintWidget, \
                                      StringFilterWidget, \
                                      ComboFilterWidget, \
                                      TagFilterWidget
from curvefinder.models import Window, CurveDB
from curvefinder.qtgui.gui import CurveCreateWidget

from numpy import array
from guiqwt import plot
from guiqwt.builder import make
import datetime
import dateutil
import json


class CurveEditor(QtGui.QMainWindow):
    def __init__(self):
        super(CurveEditor, self).__init__()
        self._filter_widget = self._get_filter_widget()
        self._list_curve_widget = self._get_list_curve_widget()
        self.addDockWidget(\
                QtCore.Qt.DockWidgetArea(QtCore.Qt.LeftDockWidgetArea), \
                self._filter_widget)
        self.addDockWidget(\
                QtCore.Qt.DockWidgetArea(QtCore.Qt.RightDockWidgetArea), \
                self._list_curve_widget)
        self._curve_display_widget = self._get_curve_display_widget()
        self.setCentralWidget(self._curve_display_widget)
        self._filter_widget.value_changed.connect(self.refresh)
        self._filter_widget.value_changed.connect(self.save_defaults)        
        self._list_curve_widget.current_item_changed.connect(self.display)
        
        
        settings = QtCore.QSettings("pyinstruments", "pyinstruments")
        default_json = str(settings.value("curve_editor_defaults").toString())
        if default_json != "":
            defaults = json.loads(default_json)
            for key in ["date_lte", "date_gte", "date_equals"]:
                enabled, val = defaults[key]
                if val:
                    defaults[key] = enabled, dateutil.parser.parse(val)
        else:
            defaults = {}
        self.set_defaults(**defaults)
        
        self.show()
    
    
    def display(self, curve):
        self._curve_display_widget.display(curve)
    
    def set_defaults(self, **kwds):
        self._filter_widget.set_defaults(**kwds)
    
    def save_defaults(self):
        defaults = self._filter_widget.get_values()
        for key in ["date_lte", "date_gte", "date_equals"]:
            enabled, val = defaults[key]
            val = str(val)
            defaults[key] = enabled, val
        defaults_json = json.dumps(defaults)
        settings = QtCore.QSettings("pyinstruments", "pyinstruments")
        settings.setValue("curve_editor_defaults", defaults_json)
    
    def refresh(self):
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
    def set_defaults(self, **kwds):
        self._widget_full.set_defaults(**kwds)
    
    def get_values(self):
        return self._widget_full.get_values()
    
    def get_query_set(self):
        return self._widget_full.get_query_set()
    
    def _get_filter_widget(self):
        class InnerFilterWidgetFull(QtGui.QWidget):
            def __init__(self, parent):
                super(InnerFilterWidgetFull, self).__init__(parent)
                self._filter_layout = QtGui.QVBoxLayout()
                self._filters = {}
                self._filters["date_equals"] = \
                    DateConstraintWidget('=', self)
                self._filters["date_lte"] = \
                    DateConstraintWidget('>=', self)
                self._filters["date_gte"] = \
                    DateConstraintWidget('<=', self)
                    
                self._filters["date_equals"].enabled_on.connect( \
                                                    self._disable_lte_gte)
                self._filters["date_lte"].enabled_on.connect( \
                                                    self._disable_equals)
                self._filters["date_gte"].enabled_on.connect( \
                                                    self._disable_equals)
                
                
                self._filters["name"] = \
                    StringFilterWidget('name', self)
                self._filters["comment"] = \
                    StringFilterWidget('comment', self)
                self._filters["window"] = \
                    ComboFilterWidget(Window, 'window', self)
                self._filters["tags"] = \
                    TagFilterWidget(self)    

            
                for name, filter in self._filters.iteritems():
                    self._filter_layout.addWidget(filter)
                    filter.value_changed.connect(self.value_changed)
                self.setLayout(self._filter_layout)
                
            value_changed = QtCore.pyqtSignal(name = "value_changed")
            
            def _disable_lte_gte(self):
                self._filters["date_lte"].enabled = False
                self._filters["date_gte"].enabled = False
                
            def _disable_equals(self):
                self._filters["date_equals"].enabled = False
            
            def get_values(self):
                values = {}
                for key, widget in self._filters.iteritems():
                    values[key] = widget.value
                return values
                
            def set_defaults(self, **kwds):
                for key, widget in self._filters.iteritems():
                    try:
                        val = kwds[key]
                    except KeyError:
                        print "no key " + key + " found" 
                    else:
                        if val:
                            widget.value = val
            
            def get_query_set(self):
                kwds = dict()
                ## first query for the required tags
                filters = self._filters.copy()
                tag_filter = filters.pop("tags")
                queryset = \
                    tag_filter.get_query_set()
                for name, filter in filters.iteritems():
                    kwds.update(filter.get_kwds_for_query())
                
                return queryset.filter(**kwds)
            
        return InnerFilterWidgetFull(self)
        
        
class ListCurveWidget(QtGui.QDockWidget, object):
    current_item_changed = QtCore.pyqtSignal(object)
    def __init__(self, parent):
        super(ListCurveWidget, self).__init__(parent)
        self._tree_widget = self._get_tree_widget()
        self.setWidget(self._tree_widget)
        self.refresh()
        self._tree_widget.currentItemChanged.connect(
                                            self._current_item_changed)
        self.setMinimumWidth(180)
    def _current_item_changed(self):
        self.current_item_changed.emit(self.selected)
    
    @property
    def selected(self):
        sel = self._tree_widget.currentItem()
        if sel:
            return CurveDB.objects.get(pk = sel.pk)
        else:
            return None
        
    def refresh(self):
        curves = self.parent().get_query_set()
        self._tree_widget.clear()
        for curve in curves:
            item = QtGui.QTreeWidgetItem([curve.name])
            item.pk = curve.pk
            self._tree_widget.addTopLevelItem(item)
    
    def _get_tree_widget(self):
        class ListTreeWidget(QtGui.QTreeWidget):
            def __init__(self, parent):
                super(ListTreeWidget, self).__init__(parent)                    
                self.headerItem().setText(0, "curve name")
        return ListTreeWidget(self)


class AllFieldDisplayWidget(QtGui.QWidget):
    def __init__(self, parent, dic):
        super(AllFieldDisplayWidget, self).__init__(parent)
        self._lay = QtGui.QGridLayout()
        self.field_display_widgets = dict()
        self.rows = 3
        row = 0
        col = 0
        for field, val in dic.iteritems():
            widget = FieldDisplayWidget(self, field, val)
            self.field_display_widgets[field] = widget
            self._lay.addWidget(widget, row, col)
            row += 1
            if row>=self.rows:
                row = 0
                col+=1
    
        self.setLayout(self._lay)
        self.setMinimumHeight(150)
        self.setMinimumWidth(600)
        self.setMaximumWidth(600)
class FieldDisplayWidget(QtGui.QWidget):
    def __init__(self, parent, field, value):
        super(FieldDisplayWidget, self).__init__(parent)
        self._lay = QtGui.QHBoxLayout()
        self.label = QtGui.QLabel(field + ' : ' + value)
        self._lay.addWidget(self.label)
        self.setLayout(self._lay)

class CurveIdWidget(QtGui.QWidget):
    def __init__(self, parent = None):
        super(CurveIdWidget, self).__init__(parent)
        self._lay = QtGui.QGridLayout()
        self.label_id = QtGui.QLabel("ID : 0000")
        font = QtGui.QFont()
        font.setPointSize(20)
        self.label_id.setFont(font)
        self._lay.addWidget(self.label_id, 0, 0)
        self.setLayout(self._lay)
        self.widget_all_fields = AllFieldDisplayWidget(self, dict())
        self._lay.addWidget(self.widget_all_fields, 0, 1)
        self.delete_button = QtGui.QPushButton("Delete...")
        self.delete_button.setMaximumWidth(100)
        self.delete_button.setMinimumHeight(150)
        self._lay.addWidget(self.delete_button, 0, 2)
        
        
    def dump_in_gui(self, curve):
        fields = curve.get_subclass_fields()
        if self.widget_all_fields:
            self.widget_all_fields.deleteLater()
        self.widget_all_fields = AllFieldDisplayWidget(self, fields)
        self._lay.addWidget(self.widget_all_fields, 0, 1)
            

class CurveDisplayWidget(QtGui.QWidget):
    def __init__(self, parent):
        super(CurveDisplayWidget, self).__init__(parent)
        self.plot_widget = plot.CurveWidget(self, 'curve graph', \
                                            show_itemlist=False)
        self.plot_widget.setMinimumHeight(450)
        self.plot_widget.plot.set_antialiasing(True)
        self.plot_widget.register_all_curve_tools()
        self._lay = QtGui.QVBoxLayout()
        
        
        
        self.curve_id_widget = CurveIdWidget(self)
        self._lay.addWidget(self.curve_id_widget)
        self._lay.addWidget(self.plot_widget)
        self.setup_plot_widget()
        self.alter_curve_widget = CurveCreateWidget(parent = self)
        self._lay.addWidget(self.alter_curve_widget)
        
        #---guiqwt curve item attribute:
        self.curve_item = make.curve([], [], color='b')
        self.plot_widget.plot.add_item(self.curve_item)
        self.setLayout(self._lay)
    
    def setup_plot_widget(self):
         #---guiqwt plot manager
        self.manager = plot.PlotManager(self)
        #---Register plot to manager
        self.manager.add_plot(self.plot_widget.plot)
        #---
        #---Add toolbar and register manager tools
        #toolbar = self.parent().addToolBar("tools")
        toolbar = QtGui.QToolBar("plot tools", self)
        self.manager.add_toolbar(toolbar, id(toolbar))
        self._lay.addWidget(toolbar)
        self.manager.register_all_curve_tools()
        #---
       
    def display(self, curve):
        if curve:
            self.curve_item.set_data(array(curve.data.index, dtype = float), \
                   array(curve.data, dtype = float))
            self.curve_item.plot().replot()
        
            self.curve_id_widget.dump_in_gui(curve)