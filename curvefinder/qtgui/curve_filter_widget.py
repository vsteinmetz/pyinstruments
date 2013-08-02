"""
defines a widget to filter curves in the database
"""

from PyQt4 import QtGui, QtCore

class CurveFinderWidget(QtGui.QWidget):
    """
    The main editor for curves
    """
    
    def __init__(self):
        pass

class FilterWidget(QtGui.QWidget):
    """
    Base class for graphical filtering element
    """
    
    def __init__(self):
        super(FilterWidget, self).__init__()
        self.layout = QtGui.QHBoxLayout()
        self._enabled_checkbox = QtGui.QCheckBox()
        self._enabled_checkbox.stateChanged.connect(self.change_enabled)
        self.layout.addWidget(self._enabled_checkbox)
        self.other_widget = self.get_other_widget()
        self.layout.addWidget(self.other_widget)
        self.setLayout(self.layout)
        self.change_enabled(self._enabled_checkbox.checkState())
    
    @property
    def enabled(self):
        return self._enabled_checkbox.checkState() == 2
    
    def change_enabled(self, new_state):
        self.other_widget.setEnabled(new_state == 2)
    
    def get_other_widget(self):
        return QtGui.QWidget()

    def fullfills(self, curve):
        if self.enabled:
            return self.other_widget.fullfills(curve)
        else:
            return True
    

class DateSelectWidget(QtGui.QWidget):
    """a widget to select a date"""
    
    def __init__(self, default = None):
        """defaults to today if no date is provided"""
        
        super(DateSelectWidget, self).__init__()
        self._lay = QtGui.QHBoxLayout()
        self._choose_button = QtGui.QPushButton("...")
        self._choose_button.clicked.connect(self._choose_date)
        self._lay.addWidget(self._choose_button)
        self._date_edit = QtGui.QDateEdit()
        self._lay.addWidget(self._date_edit)
        
        self.setLayout(self._lay)

        if default:
            self.date = default
        else:
            self.date = QtCore.QDate.currentDate()
    def _choose_date(self):
        calendar = CalendarValidateWidget(default = self.date)
        date = calendar.get_date()
        if date:
            self._date_edit.setDate(date)
        
    @property
    def date(self):
        return self._date_edit.date()
    
    @date.setter
    def date(self, date):
        self._date_edit.setDate(date)
    
class CalendarValidateWidget(QtGui.QMessageBox):
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
    def __init__(self, constraint = ">="):
        """
        Constraints can be either ">=", "<=" or "="
        """
        if constraint not in ["=", "<=", ">="]:
            raise ValueError( \
    """constraint can be either ">=", "<=" or "=", not """ + constraint)
        
        self.constraint = constraint
        super(DateConstraintWidget, self).__init__()
        
        
            
    def get_other_widget(self):
        class DateConstraintWidget(QtGui.QWidget):
            constraint = self.constraint
            def __init__(self):
                super(DateConstraintWidget, self).__init__()
                self._lay = QtGui.QHBoxLayout()
                self._bound_widget = DateSelectWidget()
                if DateConstraintWidget.constraint == ">=":
                    self._lay.addWidget(self._bound_widget)
                    self._label = QtGui.QLabel(" <= date")
                    self._lay.addWidget(self._label)
                if DateConstraintWidget.constraint == "<=":
                    self._label = QtGui.QLabel("date <= ")
                    self._lay.addWidget(self._label)
                    self._lay.addWidget(self._bound_widget)
                if DateConstraintWidget.constraint == "=":
                    self._label = QtGui.QLabel("date = ")
                    self._lay.addWidget(self._label)
                    self._lay.addWidget(self._bound_widget)
                self.setLayout(self._lay)
            
            @property
            def date(self):
                return self._bound_widget.date.toPyDate()
            
            def fullfills(self, curve):
                if DateConstraintWidget.constraint == "=":
                    return curve.date_created.date() == self.date
                if DateConstraintWidget.constraint == ">=":
                    return curve.date_created.date() >= self.date
                if DateConstraintWidget.constraint == "<=":
                    return curve.date_created.date() <= self.date
        return DateConstraintWidget()
        

class StringFilterWidget(FilterWidget):
    def __init__(self, field_name):
        """checks if curve.field_name is the requested string"""
        self.field_name = field_name
        super(StringFilterWidget, self).__init__()
        
    def get_other_widget(self):
        class StringFilterWidget(QtGui.QWidget):
            field_name = self.field_name
            
            def __init__(self):
                super(StringFilterWidget, self).__init__()
                self._lay = QtGui.QHBoxLayout()
                self._label = QtGui.QLabel(self.field_name + " = ")
                self._lay.addWidget(self._label)
                self._line = QtGui.QLineEdit()
                self._lay.addWidget(self._line)
                self.setLayout(self._lay)
            
            @property
            def value(self):
                return str(self._line.text())
                       
            def fullfills(self, curve):
                return curve.__getattribute__(self.field_name) == self.value
        return StringFilterWidget()

class ComboFilterWidget(FilterWidget):
    def __init__(self, foreignkey_name):
        """checks if curve.field_name is the requested string"""
        self.foreignkey_name = foreignkey_name
        super(ComboFilterWidget, self).__init__()

    def get_other_widget(self):
        class ComboFilterWidget(QtGui.QWidget):
            field_name = self.field_name
            
            def __init__(self):
                super(StringFilterWidget, self).__init__()
                self._lay = QtGui.QHBoxLayout()
                self._label = QtGui.QLabel(self.field_name + " = ")
                self._lay.addWidget(self._label)
                self._line = QtGui.QLineEdit()
                self._lay.addWidget(self._line)
                self.setLayout(self._lay)
            
            @property
            def value(self):
                return str(self._line.text())
                       
            def fullfills(self, curve):
                return curve.__getattribute__(self.field_name) == self.value
        return StringFilterWidget()

class TagFilterWidget(FilterWidget):
    pass

class CommentFilterWidget(FilterWidget):
    pass