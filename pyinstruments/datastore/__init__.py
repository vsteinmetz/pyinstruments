from PyQt4.QtCore import QSettings
from db_dialogs import DialogOpenDatabase, DialogNewDatabase
import os
from guidata import qapplication
APP = qapplication()

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


settings = QSettings('pyinstruments', 'pyinstruments')
db = str(settings.value('database_file').toString())
if db == "":
    dial = DialogNewDatabase()
    while not dial.exec_():
        pass
    
    settings.setValue('database_file', dial.filename)
    import subprocess
    subprocess.call(['python', 
                os.path.join(os.path.dirname(os.path.abspath(__file__)),'..', 'manage.py'),
                'syncdb', '--noinput'], shell = True)
    
    settings.setValue('database_login', dial.login)
    settings.setValue('database_password', dial.password)
    
    import django
    
    create_super_user(dial.login, dial.password)
    
