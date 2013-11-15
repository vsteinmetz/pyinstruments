from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import QSettings
import os

class DialogChooseDatabase(QtGui.QDialog):
    def __init__(self, parent=None):
        super(DialogChooseDatabase, self).__init__(parent)
        self.lay = QtGui.QHBoxLayout()
        
        self.button_existing = QtGui.QPushButton(
                            'Connect to an existing database...')
        self.button_new = QtGui.QPushButton('Create new database...')
        self.button_new.pressed.connect(self.new_database)
        self.button_existing.pressed.connect(self.existing_database)
        self.lay.addWidget(self.button_existing)
        self.lay.addWidget(self.button_new)
        self.setLayout(self.lay)
    
    def new_database(self):
        print 'new database'
        settings = QSettings('pyinstruments', 'pyinstruments')
        dial = DialogNewDatabase()
        while not dial.exec_():
            pass
        #settings.setValue('database_file', dial.filename)
        change_default_database_name(dial.filename)
        #settings.sync()
        
        import subprocess
        if subprocess.call(
                        ['python', 
                          os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                       '..',
                                       'manage.py'),
                         'syncdb',
                         '--noinput'],
                    shell=False):
            raise ValueError("problem with db synchronization")
        
        settings.setValue('database_login', dial.login)
        settings.setValue('database_password', dial.password)
        settings.sync()
        import django
        
        create_super_user(dial.login, dial.password)
        self.accepted.emit()
        self.hide()
    
    def existing_database(self):
        print 'existing database'
        settings = QSettings('pyinstruments', 'pyinstruments')
        dial = DialogOpenDatabase()
        while not dial.exec_():
            pass
        settings.setValue('database_file', dial.filename)
        settings.sync()
        self.accepted.emit()
        self.hide()
        
class DialogOpenDatabase(QtGui.QDialog):
    def __init__(self, parent=None):
        super(DialogOpenDatabase, self).__init__(parent)
        self.lay = QtGui.QVBoxLayout()
        
        #self.file_dialog = QtGui.QFileDialog(self)
        #self.file_dialog.setFileMode(QtGui.QFileDialog.AnyFile)
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
    def __init__(self, parent = None):
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
    def __init__(self, parent = None):
        super(DialogNewDatabase, self).__init__(parent)
        self.login_form = LoginForm(self)
        self.lay.insertWidget(1, self.login_form)
        self.help_widget = QtGui.QLabel("")
        self.lay.insertWidget(0, self.help_widget)
        
    validated = QtCore.pyqtSignal(name='validated')
    
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
    
    
    
def create_database():
    from django.core import management
    management.call_command('syncdb', interactive=False)
    #subprocess.call(['python', 'C:/Users/Samuel/Documents/GitHub/pyinstruments/manage.py', 'syncdb'])
### see http://stackoverflow.com/questions/1466827/
###automatically-create-an-admin-user-when-running-djangos-manage-py-syncdb
def create_super_user(login, password):
    # Create the super user and sets his password.
    from django.core import management
    management.call_command('createsuperuser', 
                            interactive=False,
                            email = 'dummy.dummy@dummy.com',
                            username=login)
    from django.contrib.auth.management.commands import changepassword
    command = changepassword.Command()
    command._get_pass = lambda *args: password
    command.execute(login)
    
def _new_database(dummy = True, cancel_allowed = True):
    dialog_new_database = DialogNewDatabase()
    if not dialog_new_database.exec_():
        if cancel_allowed:
            return
    change_default_database_name(dialog_new_database.filename)
    create_database()
    create_super_user(dialog_new_database.login,
                      dialog_new_database.password)
    
def _open_database():
    dialog_new_database = DialogOpenDatabase()
    if dialog_open_database.exec_():
        change_default_database_name(dialog_open_database.filename)    
    

def change_default_database_name(filename):
    """
    first, changes directly the 'living' dictionnary, but also stores  the value 
    for latter execution
    """
    
    #DATABASE_FILE = filename
    #DATABASES["default"]["NAME"] = filename
    settings = QSettings('pyinstruments', 'pyinstruments')
    
    settings.setValue("database_file", filename)
    settings.sync()
    if not settings.isWritable():
        raise ValueError("the file " + settings.fileName() + " cannot be modified, please change permissions")
    #MEDIA_ROOT = os.path.splitext(DATABASE_FILE)[0]
    

