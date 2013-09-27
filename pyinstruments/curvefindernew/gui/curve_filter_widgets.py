from pyinstruments.curvefindernew.gui.value_widgets import DateSelectWidget
from pyinstruments.curvefindernew import models
from pyinstruments.curvefindernew.gui.tag_filter_widget import CurveTagWidget

from PyQt4 import QtGui, QtCore
from datetime import timedelta

class MultiFilterWidget(QtGui.QWidget):
    """
    The big widget that contains all other filter widgets
    """
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
        
        self.main_lay.addWidget(self.tag_widget)
        self.main_lay.setStretchFactor(self.lay, 0)
        self.main_lay.setStretchFactor(self.tag_widget, 1)

    def query(self):
        qs = models.CurveDB.objects.all()
        for filter in self.filters:
            qs = filter.filter(qs)
        if self.tag_widget.active:
            for tag in self.tag_widget.tags:
                qs = qs.filter_tag(tag)
        return qs
    
    @property
    def n_rows(self):
        return len(self.filters)

    def add_row(self):
        gui_filter = GuiFilter(self)
        self.filters.append(gui_filter)
        gui_filter.add_all_widgets_in_layout(len(self.filters))

    def remove_filter(self, guifilter):
        row_number = self.filters.index(guifilter)
        guifilter.delete_all_widgets()


class FilterTagWidget(QtGui.QWidget):
    def __init__(self, parent=None):
        super(FilterTagWidget, self).__init__(parent)
        self.active = False
        self.tag_widget = CurveTagWidget()
        self.lay = QtGui.QHBoxLayout()
        self.setLayout(self.lay)
        self.lay.addWidget(self.tag_widget)
        self.button_filter_by_tag = QtGui.QPushButton('filter by tag')
        self.lay.addWidget(self.button_filter_by_tag)
        self.button_remove = QtGui.QPushButton('remove')
        self.lay.addWidget(self.button_remove)
        self.button_remove.pressed.connect(self.remove)
        self.button_filter_by_tag.pressed.connect(self.filter_by_tag)        
        self.remove()
        
    def filter_by_tag(self):
        self.active = True
        self.tag_widget.show()
        self.button_filter_by_tag.hide()
        self.button_remove.show()
        
    def remove(self):
        self.active = False
        self.button_remove.hide()
        self.tag_widget.hide()
        self.button_filter_by_tag.show()
    
    @property
    def tags(self):
        return self.tag_widget.tags
        
class WidgetValue(QtGui.QStackedWidget, object):
    """
    A cameleon widget that can help define a string, a bool, a date...
    """
    
    def __init__(self, parent=None):
        super(WidgetValue, self).__init__(parent)
        
        self.widget_value_stacked = dict()
        self.date_widget = DateSelectWidget()
        self.widget_value_stacked['date'] = (self.addWidget(self.date_widget),
                                             self.date_widget)
        self.string_widget = QtGui.QLineEdit()
        val = self.addWidget(self.string_widget)
    
        self.widget_value_stacked['char'] = (val,
                                            self.string_widget)
        self.widget_value_stacked['text'] = (val,
                                             self.string_widget)
        
        self.boolean_widget = QtGui.QCheckBox()
        self.widget_value_stacked['boolean'] = (self.addWidget(self.boolean_widget),
                                                self.boolean_widget)
        
        
        self.float_widget = QtGui.QDoubleSpinBox()
        self.widget_value_stacked['float'] = (self.addWidget(self.float_widget),
                                              self.float_widget)

    def update(self, type_):
        self.setCurrentIndex(self.widget_value_stacked[type_][0])

    def value(self):
        return self.currentWidget().value
    
    
class GuiFilter(object):
    def __init__(self, parent=None):
        super(GuiFilter, self).__init__()
        self.parent = parent
        self.combo_par = QtGui.QComboBox()
        for col in models.ParamColumn.objects.all():
            self.combo_par.addItem(col.name)
        self.combo_rel = QtGui.QComboBox()
        self.widget_value = WidgetValue()
        
        self.button_remove = QtGui.QPushButton('remove')
        self.button_remove.pressed.connect(self.remove)
        self.combo_par.currentIndexChanged.connect(self.update_widgets)
        self.update_widgets()
        
    def rel_string(self):
        val = {'<':'lt', '<=':'lte', '>':'gt', '>=':'gte', '=':'', 'contains':'contains'}
        return val[self.relation]
    
    def filter(self, queryset):
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
                return queryset.filter_param(self.col_name, **kwds1).filter_param(self.col_name, **kwds2)
        kwds = {query_str:value}
        return queryset.filter_param(self.col_name, **kwds)    
    
    def repopulate_combo_rel(self):
        self.combo_rel.clear()
        if self.type_of_par=='char' or self.type_of_par=='text':
            self.combo_rel.addItems(['=', 'contains'])
        if self.type_of_par=='boolean':
            self.combo_rel.addItems(['='])
        if self.type_of_par=='date' or self.type_of_par=='float':
            self.combo_rel.addItems(['=','<','<=','>','>='])
    
    def update_widgets(self):
        self.widget_value.update(self.type_of_par)
        self.repopulate_combo_rel()
    
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