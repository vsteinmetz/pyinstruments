from PyQt4 import QtCore, QtGui


class IdDisplayWidget(QtGui.QWidget):
    save_pressed = QtCore.pyqtSignal()
    delete_done = QtCore.pyqtSignal()
    
    def __init__(self, parent = None):
        super(IdDisplayWidget, self).__init__(parent)
        self.lay = QtGui.QVBoxLayout()
        self.setLayout(self.lay)
        self.form_lay = QtGui.QFormLayout()
        self.lay.addLayout(self.form_lay)
        
        self.label_id = QtGui.QLabel()
        self.form_lay.addRow('ID', self.label_id)
        self.label_name = QtGui.QLabel()
        self.form_lay.addRow('name', self.label_name)
        self.label_type = QtGui.QLabel()
        self.form_lay.addRow('type', self.label_type)
        
        font = QtGui.QFont()
        font.setPointSize(20)
        #self.label_id.setFont(font)
        
        self.delete_button = QtGui.QPushButton('Delete')
        self.delete_button.pressed.connect(self.delete)
        
        self.save_button = QtGui.QPushButton('Save')
        self.save_button.pressed.connect(self.save_pressed)
        
        self.lay.addWidget(self.delete_button)
        self.lay.addWidget(self.save_button)
        
        self.curve_displayed = None
        
    def delete(self, confirm=True):
        if not self.curve_displayed:
            return
        if confirm:
            message_box = QtGui.QMessageBox(self)
            answer = message_box.question(self, 'delete', \
                        'are you sure you want to delete curve id =' \
                        + str(self.curve_displayed.id) + ' ?', 'No', 'Yes')
            if not answer:
                return
        self.curve_displayed.delete()
        self.delete_done.emit()
    
    def display_curve(self, curve):
        self.curve_displayed = curve
        self.label_id.setText(str(curve.id))
        self.label_name.setText(curve.params["name"])
        self.label_type.setText(curve.params["curve_type"])