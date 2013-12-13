from pyinstruments.curvefinder.gui.curve_search_widget.value_widgets import DateSelectWidget, \
                                                           BooleanWidget, \
                                                           FloatWidget, \
                                                           CharWidget
from pyinstruments.curvestore import models
#from pyinstruments.curvefinder.gui.curve_search_widget.tag_filter_widget import CurveTagWidget
from pyinstruments.curvestore.tag_widget import CurveTagWidget

from PyQt4 import QtGui, QtCore
from datetime import timedelta

class MultiFilterWidget(QtGui.QWidget):
    """
    The big widget that contains all other filter widgets
    """
    
    value_changed = QtCore.pyqtSignal()
    
    def __init__(self, parent=None):
        super(MultiFilterWidget, self).__init__(parent)
        
        self.main_lay = QtGui.QVBoxLayout()
        self.setLayout(self.main_lay)
        
        self.lay = QtGui.QGridLayout()
        self.main_lay.addLayout(self.lay)
        
        
        self.add_row_button = QtGui.QPushButton("add filter")
        self.lay.addWidget(self.add_row_button, 0, 0, 1, 4)
        self.add_row_button.pressed.connect(self.add_row)
        
        self.filters = []

        self.tag_widget = FilterTagWidget()
        self.tag_widget.value_changed.connect(self.value_changed)
        
        self.main_lay.addWidget(self.tag_widget)
        self.main_lay.setStretchFactor(self.lay, 0)
        self.main_lay.setStretchFactor(self.tag_widget, 1)

        self.n_rows = 0
        
    def query(self):
        qs = models.CurveDB.objects.all()
        for filter in self.filters:
            qs = filter.filter(qs)
        if self.tag_widget.active:
            for tag in self.tag_widget.get_tags():
                qs = qs.filter_tag(tag)
        return qs
    
    def query_string(self):
        query = "CurveDB.objects"
        if self.tag_widget.active:
            for tag in self.tag_widget.get_tags():
                query+=".filter_tag(\"" +tag+"\")"
        for filter in self.filters:
            query+= filter.query_string()
        if query=="CurveDB.objects":
            query+=".all()"
        return query
    
    def add_row(self):
        self.n_rows+=1
        gui_filter = GuiFilter(self)
        gui_filter.value_changed.connect(self.value_changed)
        self.filters.append(gui_filter)
        gui_filter.add_all_widgets_in_layout(self.n_rows)
        self.value_changed.emit()

    def remove_filter(self, guifilter):
        guifilter.delete_all_widgets()
        self.filters.remove(guifilter)
        self.value_changed.emit()

class FilterTagWidget(QtGui.QWidget, object):
    value_changed = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super(FilterTagWidget, self).__init__(parent)
        self.active = False
        self.tag_widget = CurveTagWidget()
        self.lay = QtGui.QVBoxLayout()
        self.setLayout(self.lay)
        self.lay.addWidget(self.tag_widget)
        self.button_filter_by_tag = QtGui.QPushButton('filter by tag')
        self.lay.addWidget(self.button_filter_by_tag)
        self.button_remove = QtGui.QPushButton('remove \ntag filter')
        self.lay.addWidget(self.button_remove)
        self.button_remove.pressed.connect(self.remove)
        self.button_filter_by_tag.pressed.connect(self.filter_by_tag)        
        self.remove()
        self.tag_widget.value_changed.connect(self.value_changed)
        
    def filter_by_tag(self):
        self.active = True
        self.tag_widget.show()
        self.button_filter_by_tag.hide()
        self.button_remove.show()
        self.value_changed.emit()
        
    def remove(self):
        self.active = False
        self.button_remove.hide()
        self.tag_widget.hide()
        self.button_filter_by_tag.show()
        self.value_changed.emit()
        
    
    def get_tags(self):
        return self.tag_widget.get_tags()
        
class WidgetValue(QtGui.QStackedWidget, object):
    """
    A cameleon widget that can help define a string, a bool, a date...
    """
    
    value_changed = QtCore.pyqtSignal()
    
    def __init__(self, parent=None):
        super(WidgetValue, self).__init__(parent)
        
        self.widget_value_stacked = dict()
        self.date_widget = DateSelectWidget()
        self.date_widget.value_changed.connect(self.value_changed)
        self.widget_value_stacked['date'] = (self.addWidget(self.date_widget),
                                             self.date_widget)
        self.string_widget = CharWidget()
        self.string_widget.value_changed.connect(self.value_changed)
        val = self.addWidget(self.string_widget)
    
        self.widget_value_stacked['char'] = (val,
                                            self.string_widget)
        self.widget_value_stacked['text'] = (val,
                                             self.string_widget)
        
        self.boolean_widget = BooleanWidget()
        self.boolean_widget.value_changed.connect(self.value_changed)
        self.widget_value_stacked['boolean'] = (self.addWidget(self.boolean_widget),
                                                self.boolean_widget)
        
        
        self.float_widget = FloatWidget()
        self.float_widget.value_changed.connect(self.value_changed)
        self.widget_value_stacked['float'] = (self.addWidget(self.float_widget),
                                              self.float_widget)

    def update(self, type_):
        self.setCurrentIndex(self.widget_value_stacked[type_][0])

    def value(self):
        return self.currentWidget().value
    
    
class GuiFilter(QtCore.QObject, object):
    value_changed = QtCore.pyqtSignal()
    
    def __init__(self, parent=None):
        super(GuiFilter, self).__init__()
        self.parent = parent
        self.combo_par = QtGui.QComboBox()
        self.combo_par.setMaximumWidth(100)
        for col in models.ParamColumn.objects.all():
            self.combo_par.addItem(col.name)
        self.combo_rel = QtGui.QComboBox()
        self.combo_rel.setMaximumWidth(40)
        self.widget_value = WidgetValue()
        self.widget_value.setMaximumWidth(100)
        
        self.button_remove = QtGui.QPushButton('del')
        self.button_remove.setMaximumWidth(40)
        self.button_remove.pressed.connect(self.remove)
        self.combo_par.currentIndexChanged.connect(self.update_widgets)
        self.update_widgets()
    
        self.widget_value.value_changed.connect(self.value_changed)
        self.combo_rel.currentIndexChanged.connect(self.value_changed)
        
    def rel_string(self):
        val = {'<':'lt', '<=':'lte', '>':'gt', '>=':'gte', '=':'', 'contains':'contains'}
        return val[self.relation]
    
    def query_string_dict(self):
        rel_string = self.rel_string()
        if rel_string != '':
            rel_string = '__' + rel_string
        query_str = 'value' + rel_string
        value = self.value
        
        if self.type_of_par == "date":
            if self.relation == '<=':
                value += timedelta(days = 1)
            if self.relation == '>':
                value += timedelta(days = 1)
            if self.relation == '=':
                kwds1 = {'value__gte':value}
                kwds2 = {'value__lte':value + timedelta(days = 1)}
                return kwds1, kwds2
                #return queryset.filter_param(self.col_name, **kwds1).filter_param(self.col_name, **kwds2)
        return {query_str:value}
        
    def query_string(self):
        kwds = self.query_string_dict()
        if isinstance(kwds, tuple):
            kwds1, kwds2 = kwds
            return ".filter_param(" + self.col_name + ", " + kwds1.keys()[0] + "=" + str(kwds1.values()[0]) + ").filter_param(" + self.col_name +  ", " + kwds2.keys()[0] + "=" + str(kwds2.values()[0]) + ")"
        return ".filter_param(" + self.col_name + ", " + kwds.keys()[0] + "=" + str(kwds.values()[0]) + ")"  
    
    def filter(self, queryset):
        kwds = self.query_string_dict()
        if isinstance(kwds, tuple):
            kwds1, kwds2 = kwds
            return queryset.filter_param(self.col_name, **kwds1).filter_param(self.col_name, **kwds2)
        return queryset.filter_param(self.col_name, **kwds)    
    
    def repopulate_combo_rel(self):
        self.combo_rel.blockSignals(True)
        self.combo_rel.clear()
        if self.type_of_par=='char' or self.type_of_par=='text':
            self.combo_rel.addItems(['=', 'contains'])
        if self.type_of_par=='boolean':
            self.combo_rel.addItems(['='])
        if self.type_of_par=='date' or self.type_of_par=='float':
            self.combo_rel.addItems(['=','<','<=','>','>='])
        self.combo_rel.blockSignals(False)
        
    def update_widgets(self):
        self.widget_value.update(self.type_of_par)
        self.repopulate_combo_rel()
        self.value_changed.emit()
    
    def delete_all_widgets(self):
        self.combo_par.deleteLater()
        self.combo_rel.deleteLater()
        self.widget_value.deleteLater()
        self.button_remove.deleteLater()
    
    #def remove_all_widgets_from_layout(self):
     #   self.parent.lay.removeWidget(self.combo_par)
     #   self.parent.lay.removeWidget(self.combo_rel)
      #  self.parent.lay.removeWidget(self.widget_value)
      #  self.parent.lay.removeWidget(self.button_remove)
        
    def add_all_widgets_in_layout(self, row):
        row = row + 1 # there is one row for button "add filter"
        self.parent.lay.addWidget(self.combo_par, row, 0)
        self.parent.lay.addWidget(self.combo_rel, row, 1)
        self.parent.lay.addWidget(self.widget_value, row, 2)
        self.parent.lay.addWidget(self.button_remove, row, 3)
    
    def remove(self):
        self.parent.remove_filter(self)
    @property
    def col_name(self):
        return self.combo_par.currentText()
    
    @property
    def col(self):
        return models.ParamColumn.objects.get(name=self.col_name)
    
    @property
    def type_of_par(self):
        return self.col.type
    
    @property
    def relation(self):
        return str(self.combo_rel.currentText())

    @property
    def value(self):
        return self.widget_value.value()
