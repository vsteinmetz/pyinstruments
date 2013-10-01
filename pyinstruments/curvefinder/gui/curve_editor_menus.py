import pyinstruments.datastore.settings
from pyinstruments.curvestore import models
from curve import Curve
import curve

import time
import os
import guidata
from PyQt4 import QtCore, QtGui
from zipfile import ZipFile
from django.core.exceptions import ObjectDoesNotExist
        
class MenuFile(QtGui.QMenu):
    def __init__(self, parent, widget):
        super(MenuFile, self).__init__(parent)        
        self.quit = QtGui.QAction(widget)
        self.quit.setText('quit')
        self.quit.triggered.connect(self._quit)
        self.addAction(self.quit)

    def _quit(self):
        guidata.qapplication().quit()
        
class MenuDB(QtGui.QMenu):
    def __init__(self, parent, widget):
        super(MenuDB, self).__init__(parent)
        self.forget_database_location = QtGui.QAction(widget)
        self.forget_database_location.setText('forget database location...')
        self.forget_database_location.triggered.connect(self._forget_db_location)
        self.addAction(self.forget_database_location)
        
        self.open_django_admin = QtGui.QAction(widget)
        self.open_django_admin.setText('open django admin')
        self.open_django_admin.triggered.connect(self._open_django_admin)
        self.addAction(self.open_django_admin)
        
        self.backup_all_files = QtGui.QAction(widget)
        self.backup_all_files.setText('backup all files...')
        self.backup_all_files.triggered.connect(
                                        self._backup_all_files)
        self.addAction(self.backup_all_files)
        
        self.import_h5_files = QtGui.QAction(widget)
        self.import_h5_files.setText('import h5 files...')
        self.import_h5_files.triggered.connect(self._import_h5_files)
        self.addAction(self.import_h5_files)
        
    
    def _backup_all_files(self):
        dial = QtGui.QFileDialog()
        filename = str(dial.getSaveFileName(parent=self))
        if not filename:
            return
        #with ZipFile(filename, 'w') as zpf:
        #    db_file = pyinstruments.datastore.settings.DATABASE_FILE
        #    zpf.write(db_file, os.path.split(db_file)[-1] + "_saved")
        for curve in models.CurveDB.objects.all():
            curve.data
            curve.params
            directo = os.path.dirname(os.path.join(filename, curve.data_file.name))
            if not os.path.exists(directo):
                os.makedirs(directo)
            Curve.save(curve, os.path.join(filename, curve.data_file.name))
         
    def _import_h5_files(self):
        """
        Import all .h5 files from a directory and subdirectories.
        """
        dial = QtGui.QFileDialog()
        dirname = str(dial.getExistingDirectory(parent=self))
        if not dirname:
            return
        
        def archive_dir(arg, dirname, files):
            for filename in files:
                fname = os.path.join(dirname, filename)
                if os.path.isfile(fname):
                    if fname.endswith('.h5'):
                        cur = curve.load(fname)
                        cur_db = models.curve_db_from_curve(cur)
                        id = int(cur.params['id'])
                        try:
                            old_one = models.CurveDB.objects.get(id=id)
                        except ObjectDoesNotExist:
                            cur_db.save()
                            cur_db.id = cur.params['id']
                        else:
                            message = "A curve with the id " + str(id) + \
                            " allready exists in your database." + "\n What should we do with curve " + \
                            cur.params["name"] + " ?"
                            
                            message_box = QtGui.QMessageBox(self)
                            answer = message_box.question(self, 'existing id', message, 'forget about it', 'overwrite ' + old_one.params['name'], "use new id")
                            
                            if answer==0:
                                continue
                            if answer==1:
                                cur_db.id = cur.params['id']
                                cur_db.save()
                            if answer==2:
                                cur_db.save()
                        
        os.path.walk(dirname, archive_dir, None)

    
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
        self.menu_file_action = QtGui.QAction('file', parent)
        self.menu_file = MenuFile(self, parent)
        self.menu_file_action.setMenu(self.menu_file)
        
        self.menu_db_action = QtGui.QAction('database', parent)
        self.menu_db = MenuDB(self, parent)
        self.menu_db_action.setMenu(self.menu_db)
        
        self.addAction(self.menu_file_action)
        self.addAction(self.menu_db_action)
        

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