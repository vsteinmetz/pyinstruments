


import datastore.settings

from PyQt4 import QtCore, QtGui
from django.contrib.auth.management.commands import changepassword
from django.core import management

class DialogOpenDatabase(QtGui.QDialog):
    def __init__(self, parent):
        super(DialogOpenDatabase, self).__init__(parent)
        self.lay = QtGui.QVBoxLayout()
        
        self.file_dialog = QtGui.QFileDialog(self)
        self.file_dialog.setFileMode(QtGui.QFileDialog.AnyFile)
        self.label = QtGui.QLabel('database file')
        self.db_location_edit = QtGui.QLineEdit()
        self.db_browse_button = QtGui.QPushButton('browse')
        self.layout_file = QtGui.QHBoxLayout()
        self.layout_file.addWidget(self.label)
        self.layout_file.addWidget(self.db_location_edit)
        self.layout_file.addWidget(self.db_browse_button)
        self.lay.addLayout(self.layout_file)
        
        self.confirm_layout = QtGui.QHBoxLayout()
        self.ok_button = QtGui.QPushButton('OK')
        
        self.cancel_button = QtGui.QPushButton('Cancel')
        
        self.connect_buttons_to_slots()
        
        
        self.confirm_layout.addWidget(self.cancel_button)
        self.confirm_layout.addWidget(self.ok_button)
        self.lay.addLayout(self.confirm_layout)
        self.setLayout(self.lay)
        self.db_browse_button.pressed.connect(self.browse)
        
    def connect_buttons_to_slots(self):
        self.cancel_button.pressed.connect(self.reject)
        self.ok_button.pressed.connect(self.accept)
        
    def browse(self):
        self.filename = QtGui.QFileDialog.getOpenFileName(self, filter = "*.db")
        
    @property
    def filename(self):
        return str(self.db_location_edit.text())
    
    @filename.setter
    def filename(self, val):
        self.db_location_edit.setText(val)
        return val

class LoginForm(QtGui.QWidget):
    def __init__(self, parent):
        super(LoginForm, self).__init__(parent)
        self.lay = QtGui.QFormLayout()
        
        self.login_edit = QtGui.QLineEdit()
        self.lay.addRow('login', self.login_edit)
        
        self.password_edit = QtGui.QLineEdit()
        self.password_edit.setEchoMode(QtGui.QLineEdit.Password)
        
        self.password_confirm = QtGui.QLineEdit()
        self.password_confirm.setEchoMode(QtGui.QLineEdit.Password)
        
        self.lay.addRow('password', self.password_edit)
        self.lay.addRow('confirm pwd', self.password_confirm)
        
        self.setLayout(self.lay)
            
class DialogNewDatabase(DialogOpenDatabase):
    def __init__(self, parent):
        super(DialogNewDatabase, self).__init__(parent)
        self.login_form = LoginForm(self)
        self.lay.insertWidget(1, self.login_form)
        self.help_widget = QtGui.QLabel("")
        self.lay.insertWidget(0, self.help_widget)
        
    validated = QtCore.pyqtSignal(name = 'validated')
    
    def connect_buttons_to_slots(self):
        self.cancel_button.pressed.connect(self.reject)
        self.ok_button.pressed.connect(self.ok_clicked)
        self.validated.connect(self.accept)
    
    def ok_clicked(self):
        if self.validate():
            self.help_widget.hide()
            self.validated.emit()
        else:
            self.help_widget.show()
    
    def browse(self):
        self.filename = QtGui.QFileDialog.getSaveFileName(self, filter = "*.db")
        
    @property
    def login(self):
        return str(self.login_form.login_edit.text())

    @property
    def password(self):
        return str(self.login_form.password_edit.text())
    
    @property
    def password_confirm(self):
        return str(self.login_form.password_confirm.text())
    
    def validate(self):
        if len(self.login)<3:
            self.help_widget.setText("3 letters minimum in login !")
            return False
        
        if self.password!=self.password_confirm:
            self.help_widget.setText("enter the same password twice please !")
            return False
        
        if len(self.password)<3:
            self.help_widget.setText("3 letters minimum in password !")
            return False
        return True
    
    def exec_(self):
        self.help_widget.hide()
        return super(DialogNewDatabase, self).exec_()
        
class MenuFile(QtGui.QMenu):
    def __init__(self, parent, widget):
        super(MenuFile, self).__init__(parent)
        self.new_database = QtGui.QAction(widget)
        self.new_database.setText('new database...')
        self.new_database.triggered.connect(self._new_database)
        
        self.open_database = QtGui.QAction(widget)
        self.open_database.setText('open database...')
        self.open_database.triggered.connect(self._open_database)
        
        self.addAction(self.new_database)
        self.addAction(self.open_database)
        
        self.dialog_new_database = DialogNewDatabase(widget)
        self.dialog_open_database = DialogOpenDatabase(widget)
    
    def set_default_database(self, filename):
        datastore.settings.change_default_databse_name(filename)
    
    def create_database(self):
        management.call_command('syncdb', interactive=False)

### see http://stackoverflow.com/questions/1466827/
###automatically-create-an-admin-user-when-running-djangos-manage-py-syncdb
    def create_super_user(self, login, password):
        # Create the super user and sets his password.
        management.call_command('createsuperuser', 
                                interactive=False,
                                email = 'dummy.dummy@dummy.com',
                                username=login)
        command = changepassword.Command()
        command._get_pass = lambda *args: password
        command.execute(login)
        
    def _new_database(self, dummy = False, cancel_allowed = True):
        if not self.dialog_new_database.exec_():
            if cancel_allowed:
                return
        self.set_default_database(self.dialog_new_database.filename)
        self.create_database()
        self.create_super_user(self.dialog_new_database.login,
                               self.dialog_new_database.password)
    def _open_database(self):
        if self.dialog_open_database.exec_():
            self.set_default_database(self.dialog_open_database.filename)
    
class CurveEditorMenuBar(QtGui.QMenuBar):    
    def __init__(self, parent):
        super(CurveEditorMenuBar, self).__init__(parent)
        self.menu_file_action = QtGui.QAction('file',parent)
        self.menu_file = MenuFile(self, parent)
        self.menu_file_action.setMenu(self.menu_file)
        self.addAction(self.menu_file_action)
        

class CurveEditorToolBar(QtGui.QToolBar, object):
    popup_unread_activated = QtCore.pyqtSignal(\
                                            name='popup_unread_activated')
    popup_unread_deactivated = QtCore.pyqtSignal(\
                                        name = 'popup_unread_deactivated')

    def __init__(self, parent):
        super(CurveEditorToolBar, self).__init__(parent)
        self._checkbox_popup_unread = NamedCheckBox(self, \
                                                    'popup unread curves')
        self.addWidget(self._checkbox_popup_unread)
        self._checkbox_popup_unread.checked.connect(self.popup_unread_activated)
        self._checkbox_popup_unread.unchecked.connect(\
                                        self.popup_unread_deactivated)
    
class NamedCheckBox(QtGui.QWidget):
    def __bool__(self):
        return self.check_state
    __nonzero__=__bool__
    
    def __init__(self, parent, label):
        super(NamedCheckBox, self).__init__(parent)
        self._lay = QtGui.QFormLayout()
        self.label = QtGui.QLabel(label)
        self.checkbox = QtGui.QCheckBox()
        self._lay.addRow(self.label, self.checkbox)
        self.setLayout(self._lay)
        self.checkbox.stateChanged.connect(self._state_changed)
    
    @property
    def check_state(self):
        return self.checkbox.checkState() == 2
    
    def _state_changed(self):
        if self.check_state:
            self.checked.emit()
        else:
            self.unchecked.emit()
    
    checked = QtCore.pyqtSignal(name='checked')
    unchecked = QtCore.pyqtSignal(name='unchecked')