from PyQt4 import QtCore, QtGui

class HBoxLayoutTight(QtGui.QHBoxLayout):
    def __init__(self, parent = None):
        super(HBoxLayoutTight, self).__init__(parent)
        self.setContentsMargins(0, 0, 0, 0)
        
        
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
    
    @property
    def value(self):
        return self.date
    
    
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
        
        
