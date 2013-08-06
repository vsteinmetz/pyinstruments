"""
defines a widget to filter curves in the database
"""

from PyQt4 import QtGui, QtCore
from datetime import timedelta

from curvefinder.qtgui.gui import CurveTagWidget
from curvefinder.models import CurveDB


class HBoxLayoutTight(QtGui.QHBoxLayout):
    def __init__(self, parent = None):
        super(HBoxLayoutTight, self).__init__(parent)
        self.setContentsMargins(0, 0, 0, 0)


class FilterWidget(QtGui.QWidget, object):
    """
    Base class for graphical filtering element
    """
    
    def __init__(self, parent):
        super(FilterWidget, self).__init__(parent)
        self.layout = HBoxLayoutTight()
        self._enabled_checkbox = QtGui.QCheckBox()
        self._enabled_checkbox.stateChanged.connect(self.change_enabled)
        self.layout.addWidget(self._enabled_checkbox)
        self.other_widget = self.get_other_widget()
        self.layout.addWidget(self.other_widget)
        self.setLayout(self.layout)
        self.change_enabled(self._enabled_checkbox.checkState())
    
        self.other_widget.value_changed.connect(self.value_changed)
        self._enabled_checkbox.stateChanged.connect(self.value_changed)
        self._enabled_checkbox.stateChanged.connect(self.enabled_changed)
        self.enabled_changed.connect(self._enabled_changed)
    
    @property
    def enabled(self):
        return self._enabled_checkbox.checkState() == 2
    
    @enabled.setter
    def enabled(self, val):
        self._enabled_checkbox.setChecked(val)
        return val
    
    @property
    def value(self):
        return self.enabled, self.other_widget.value
    
    @value.setter
    def value(self, val):
        self.enabled, self.other_widget.value = val
        return val
    
    def change_enabled(self, new_state):
        self.other_widget.setEnabled(new_state == 2)
    
    def get_other_widget(self):
        return QtGui.QWidget()

    def fullfills(self, curve):
        if self.enabled:
            return self.other_widget.fullfills(curve)
        else:
            return True
    
    def get_kwds_for_query(self):
        if self.enabled:
            return self.other_widget.get_kwds_for_query()
        else:
            return dict()
    def _enabled_changed(self):
        if self.enabled:
            self.enabled_on.emit()
    value_changed = QtCore.pyqtSignal(name = "value_changed")
    enabled_on = QtCore.pyqtSignal(name = "enabled_on")
    enabled_changed = QtCore.pyqtSignal(name = "enabled_changed")

class DummyLabel(QtGui.QLabel, object):
    value_changed = QtCore.pyqtSignal(name = 'value_changed') 

    value = True #dummy
class BoolFilterWidget(FilterWidget):
    def __init__(self, name, bool_condition, label, parent):
        self.name = name
        self.label = label
        self.bool_condition = bool_condition
        super(BoolFilterWidget, self).__init__(parent)
        
        
    def get_other_widget(self):
        return DummyLabel(self.label)
 
    def get_kwds_for_query(self):
        return {self.name: self.bool_condition}
 
class DateSelectWidget(QtGui.QWidget, object):
    """a widget to select a date"""
    
    def __init__(self, default = None, parent = None):
        """defaults to today if no date is provided"""
        
        super(DateSelectWidget, self).__init__(parent)
        self._lay = HBoxLayoutTight()
        self._date_edit = QtGui.QDateEdit()
        self._lay.addWidget(self._date_edit)
        self._choose_button = QtGui.QPushButton("...")
        self._choose_button.setMinimumWidth(30)
        self._choose_button.setMaximumWidth(30)
        self._choose_button.clicked.connect(self._choose_date)
        self._lay.addWidget(self._choose_button)
        
        self._date_edit.dateTimeChanged.connect(self.value_changed)
        self.setLayout(self._lay)

        if default:
            self.date = default
        else:
            self.date = QtCore.QDate.currentDate().toPyDate()
    
    value_changed = QtCore.pyqtSignal(name = "value_changed")
    
    def _choose_date(self):
        calendar = CalendarValidateWidget(default = self.date)
        date = calendar.get_date().toPyDate()
        if date:
            self.date = date
        
    @property
    def date(self):
        return self._date_edit.date().toPyDate()
    
    @date.setter
    def date(self, date):
        self._date_edit.setDate(QtCore.QDate(date.year, \
                                             date.month, \
                                             date.day))
    
    
    
class CalendarValidateWidget(QtGui.QMessageBox, object):
    def __init__(self, default = None):
        super(CalendarValidateWidget, self).__init__()
        self.addButton("Cancel", QtGui.QMessageBox.RejectRole)
        self.addButton("OK", QtGui.QMessageBox.AcceptRole)
        self._lay = self.layout()
        self._calendar = QtGui.QCalendarWidget()
        if default:
            self._calendar.setSelectedDate(default)
        self._lay.addWidget(self._calendar, 0, 0)
        
    def get_date(self):
        if self.exec_():
            return self._calendar.selectedDate()
        
        
    
class DateConstraintWidget(FilterWidget):
    """
    Lower and upper bound on the date
    """
    def __init__(self, constraint, parent):
        """
        Constraints can be either ">=", "<=" or "="
        """
        if constraint not in ["=", "<=", ">="]:
            raise ValueError( \
    """constraint can be either ">=", "<=" or "=", not """ + constraint)
        
        self.constraint = constraint
        super(DateConstraintWidget, self).__init__(parent)
        

    
    
            
    def get_other_widget(self):
        class InnerDateConstraintWidget(QtGui.QWidget, object):
            constraint = self.constraint
            
            @property
            def date(self):
                return self._bound_widget.date
            
            @date.setter
            def date(self, new_date):
                self._bound_widget.date = new_date
                return new_date
            
            @property
            def value(self):
                return self.date
            
            @value.setter
            def value(self, new_date):
                self.date = new_date
                return new_date
            
            def __init__(self, parent):
                super(InnerDateConstraintWidget, self).__init__(parent)
                self._lay = HBoxLayoutTight()
                self._bound_widget = DateSelectWidget()
                if self.constraint == ">=":
                    self._label = QtGui.QLabel("date >=")
                    self._lay.addWidget(self._label)
                    self._lay.addWidget(self._bound_widget)
                if self.constraint == "<=":
                    self._label = QtGui.QLabel("date <= ")
                    self._lay.addWidget(self._label)
                    self._lay.addWidget(self._bound_widget)
                if self.constraint == "=":
                    self._label = QtGui.QLabel("date = ")
                    self._lay.addWidget(self._label)
                    self._lay.addWidget(self._bound_widget)
                self.setLayout(self._lay)
                self._bound_widget.value_changed.connect( \
                                            self.value_changed)
            
            value_changed = QtCore.pyqtSignal(name = 'value_changed')
            
                        
            def get_kwds_for_query(self):
                if self.constraint == '>=':
                    return {"date_created__gte":self.date}
                if self.constraint == '<=':
                    return {"date_created__lte":self.date + \
                                                    timedelta(days = 1)}
                if self.constraint == '=':
                    return {"date_created__gte":self.date, \
                            "date_created__lte":self.date + \
                                                    timedelta(days = 1)}
            
            def fullfills(self, curve):
                if DateConstraintWidget.constraint == "=":
                    return curve.date_created.date() == self.date
                if DateConstraintWidget.constraint == ">=":
                    return curve.date_created.date() >= self.date
                if DateConstraintWidget.constraint == "<=":
                    return curve.date_created.date() <= self.date
        return InnerDateConstraintWidget(self)
        

class StringFilterWidget(FilterWidget):
    def __init__(self, field_name, parent):
        """checks if curve.field_name is the requested string"""
        self.field_name = field_name
        super(StringFilterWidget, self).__init__(parent)
    
    def get_other_widget(self):
        class InnerStringFilterWidget(QtGui.QWidget, object):
            field_name = self.field_name
            
            def __init__(self, parent):
                super(InnerStringFilterWidget, self).__init__(parent)
                self._lay = HBoxLayoutTight()
                self._label = QtGui.QLabel(self.field_name + " = ")
                self._lay.addWidget(self._label)
                self._line = QtGui.QLineEdit()
                self._lay.addWidget(self._line)
                self.setLayout(self._lay)
                self._line.editingFinished.connect( \
                                            self.value_changed)
            
            value_changed = QtCore.pyqtSignal(name = 'value_changed')
            
            @property
            def value(self):
                return str(self._line.text())
             
            @value.setter
            def value(self, val):
                self._line.setText(val)
                return val
             
            def get_kwds_for_query(self):
                if '*' in self.value:
                    value = '^' + self.value.replace('*', '(.*)') + '$'
                    key = self.field_name + '__regex'
                else:
                    value = '^' + self.value + '$'
                    key = self.field_name
                return {key:value}
                      
            def fullfills(self, curve):
                return curve.__getattribute__(self.field_name) == self.value
        return InnerStringFilterWidget(self)

class ComboFilterWidget(FilterWidget):
    def __init__(self, db_class, foreignkey_name, parent):
        """checks if curve.field_name is the requested string"""
        self.foreignkey_name = foreignkey_name
        self.db_class = db_class
        super(ComboFilterWidget, self).__init__(parent)

    def get_other_widget(self):
        class InnerComboFilterWidget(QtGui.QWidget, object):
            field_name = self.foreignkey_name
            db_class = self.db_class
            
            def __init__(self, parent):
                super(InnerComboFilterWidget, self).__init__(parent)
                self._lay = HBoxLayoutTight()
                self._label = QtGui.QLabel(self.field_name + " = ")
                self._lay.addWidget(self._label)
                self._combo = QtGui.QComboBox()
                self._lay.addWidget(self._combo)
                self.setLayout(self._lay)
                self.refresh()
                self._combo.currentIndexChanged.connect( \
                                            self.value_changed)
            
            value_changed = QtCore.pyqtSignal(name = 'value_changed')
            
            def refresh(self):
                self._combo.clear()
                for val in self.db_class.objects.all():
                    self._combo.addItem(val.name)
            
            @property
            def value(self):
                return str(self._combo.currentText())
                
            @value.setter
            def value(self, val):
                index = self._combo.findText(val)
                self._combo.setCurrentIndex(index)
                
            def get_kwds_for_query(self):
                return {self.field_name + "__name":self.value}
                   
            def fullfills(self, curve):
                return curve.__getattribute__(self.field_name) == self.value
        return InnerComboFilterWidget(self)

class TagFilterWidget(FilterWidget):
    def __init__(self, parent):
        """checks if curve.field_name is the requested string"""
        super(TagFilterWidget, self).__init__(parent)
        
    def get_query_set(self):
        if self.enabled:
            return CurveDB.objects.filter_tags_required(*self.other_widget.tags)
        else:
            return CurveDB.objects.all()
    def get_other_widget(self):
        class InnerTagFilterWidget(CurveTagWidget):
            @property
            def value(self):
                return self.tags
            
            @value.setter
            def value(self, val):
                self.tags = val
                     
        return InnerTagFilterWidget(self)