from PyQt4.QtCore import QSettings
from db_dialogs import DialogChooseDatabase
import os
from guidata import qapplication
APP = qapplication()

def create_super_user(login, password):
    # Create the super user and sets his password.
    from django.core import management
    management.call_command('createsuperuser', 
                            interactive=False,
                            email='dummy.dummy@dummy.com',
                            username=login)
    from django.contrib.auth.management.commands import changepassword
    command = changepassword.Command()
    command._get_pass = lambda *args: password
    command.execute(login)


settings = QSettings('pyinstruments', 'pyinstruments')
db = str(settings.value('database_file').toString())
if db == "":
    dial = DialogChooseDatabase()
    dial.exec_()
    
