from pyinstruments.curvestore import models
from django.db.models import ObjectDoesNotExist

from PyQt4 import QtCore, QtGui

def val_from_string(string, type_=None):
    if type_ is None:
        try:
            val = float(string)
        except ValueError:
            pass
        else:
            return val
        try:
            val = bool(string)
        except ValueError:
            pass
        else:
            return val
        return string
    else:
        if type_ == "bool":
            return bool(string)
        if type_ == "float":
            return float(string)
        return string

class AddParamDialog(QtGui.QDialog):
    def __init__(self, parent=None):
        super(AddParamDialog, self).__init__(parent)
        
        self.model = QtGui.QStringListModel()
        self.model.setStringList([col.name for col in models.ParamColumn.objects.all()])
        self.param_name_completer = QtGui.QCompleter()
        self.param_name_completer.setModel(self.model)
        self.param_name_line = QtGui.QLineEdit()
        self.param_value_line = QtGui.QLineEdit()
        
        self.button_cancel = QtGui.QPushButton("cancel")
        self.button_ok = QtGui.QPushButton("OK")
        
        self.button_cancel.clicked.connect(self.reject)
        self.button_ok.clicked.connect(self.validate)
        
        self.param_name_line.setCompleter(self.param_name_completer)
        
        self.setup_ui()
        
    def get_param_name(self):
        return str(self.param_name_line.text())
    
    def get_param_val(self):
        string = str(self.param_value_line.text())
        try:
            col = models.ParamColumn.objects.get(name=self.get_param_name())
        except ObjectDoesNotExist:
            val = val_from_string(string)
        else:
            val = val_from_string(string, col.type)
        return val
    
    def validate(self):
        name = self.get_param_name()
        self.parent().displayed_curve.params[name] = self.get_param_val()
        #self.parent().display_curve(self.parent().displayed_curve)
        self.parent().curve_modified.emit()
        self.accept()
        
    def setup_ui(self):
        self.lay = QtGui.QVBoxLayout()
        self.form_lay = QtGui.QFormLayout()
        self.label_name = QtGui.QLabel("name")
        self.label_value = QtGui.QLabel("value")
        self.form_lay.addRow(self.label_name, self.param_name_line)
        self.form_lay.addRow(self.label_value, self.param_value_line)
        self.form_lay.addRow(self.button_cancel, self.button_ok)
        self.lay.addLayout(self.form_lay)
        self.setLayout(self.lay)
        
class ParamsDisplayWidget(QtGui.QWidget):
    curve_modified = QtCore.pyqtSignal()
    
    def __init__(self, parent=None):
        super(ParamsDisplayWidget, self).__init__(parent)
        self.lay = QtGui.QVBoxLayout()
        self.tree = QtGui.QTreeWidget()
        self.tree.setSortingEnabled(True)
        self.lay.addWidget(self.tree)
        self.setLayout(self.lay)
        self.tree.setHeaderLabels(["column name", "value"])
        self.tree.setColumnWidth(0,150)
        self.tree.setColumnWidth(1,150)
        self.setMinimumWidth(200)
        self.button_add_param = QtGui.QPushButton("add a param...")
        self.button_add_param.clicked.connect(self.add_param)
        self.lay.addWidget(self.button_add_param)
        self.displayed_curve = None
    
    def refresh(self):
        self.display_curve(self.displayed_curve)
    
    def add_param(self):
        dial = AddParamDialog(self)
        dial.exec_()
        
    def format_nicely(self, val):
        return str(val)[:255]
    
    def display_curve(self, curve):
        if curve is not None:
            self.displayed_curve = curve
            self.tree.clear()
            for name, val in curve.params.iteritems():
                self.tree.addTopLevelItem(QtGui.QTreeWidgetItem([name, self.format_nicely(val)]))
        

