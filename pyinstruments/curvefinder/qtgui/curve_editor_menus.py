
import pyinstruments.datastore.settings

import time
import os
import guidata
from PyQt4 import QtCore, QtGui
from zipfile import ZipFile
        
class MenuFile(QtGui.QMenu):
    def __init__(self, parent, widget):
        super(MenuFile, self).__init__(parent)
        self.forget_database_location = QtGui.QAction(widget)
        self.forget_database_location.setText('forget database location...')
        self.forget_database_location.triggered.connect(self._forget_db_location)
        self.addAction(self.forget_database_location)
        
        self.open_django_admin = QtGui.QAction(widget)
        self.open_django_admin.setText('open django admin')
        self.open_django_admin.triggered.connect(self._open_django_admin)
        self.addAction(self.open_django_admin)
        
        self.zip_database_and_files = QtGui.QAction(widget)
        self.zip_database_and_files.setText('zip database and files...')
        self.zip_database_and_files.triggered.connect(
                                        self._zip_database_and_files)
        self.addAction(self.zip_database_and_files)
        
        self.quit = QtGui.QAction(widget)
        self.quit.setText('quit')
        self.quit.triggered.connect(self._quit)
        self.addAction(self.quit)
    
    
    def _zip_database_and_files(self):
        dial = QtGui.QFileDialog()
        filename = str(dial.getSaveFileName(parent = self, filter = '*.zip'))
        if filename:
            with ZipFile(filename, 'w') as zpf:
                db_file = pyinstruments.datastore.settings.DATABASE_FILE
                zpf.write(db_file, os.path.split(db_file)[-1])
                
                rootdir = os.path.splitext(db_file)[0]
                root_dir_minus_one = os.path.split(rootdir)[0]
                
                def archive_dir(zip_file, dirname, files):
                    for filename in files:
                        full_file_path = os.path.join(dirname, filename)
                        zip_file.write(full_file_path,
                                       os.path.join(os.path.relpath(full_file_path, 
                                                       root_dir_minus_one)))
                os.path.walk(rootdir, archive_dir, zpf)
        
    def _quit(self):
        guidata.qapplication().quit()
    
    def _open_django_admin(self):
        import subprocess
        subprocess.Popen([   'python', 
                            os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                '..',
                                '..',
                                'manage.py'),
                            'runserver'], shell = True)
        time.sleep(10)
        desktop_services = QtGui.QDesktopServices()
        desktop_services.openUrl(QtCore.QUrl('http://localhost:8000/admin'))
        
    def  _forget_db_location(self):
        settings = QtCore.QSettings('pyinstruments', 'pyinstruments')
        settings.setValue('database_file', "")
        dial = QtGui.QMessageBox.information(self,
                                             'change-database',
                                             'change will take effect at the next startup')


    
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
                                        name='popup_unread_deactivated')

    def __init__(self, parent):
        super(CurveEditorToolBar, self).__init__(parent)
        self._checkbox_popup_unread = NamedCheckBox(self,
                                                    'popup unread curves')
        self.addWidget(self._checkbox_popup_unread)
        self._checkbox_popup_unread.checked.connect(self.popup_unread_activated)
        self._checkbox_popup_unread.unchecked.connect(\
                                        self.popup_unread_deactivated)
        
        self._checkbox_plot_popups = NamedCheckBox(self,
                                                   'plot popups')
        self.addWidget(self._checkbox_plot_popups)

    
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