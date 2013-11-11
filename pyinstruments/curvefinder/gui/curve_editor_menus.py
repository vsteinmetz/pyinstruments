import pyinstruments.datastore.settings
from pyinstruments.datastore.settings import MEDIA_ROOT
from pyinstruments.curvestore import models
from pyinstruments.curvestore.import_export import import_h5_files, update_all_files, forget_db_location, reset_db, clear_db, sync_db
from curve import Curve
import curve
from pyinstruments.datalogger.models import datalogger_backup, datalogger_recovery
from pyinstruments.curvefinder import _APP

import time
import os
import guidata
from PyQt4 import QtCore, QtGui
from zipfile import ZipFile
from django.core.exceptions import ObjectDoesNotExist
import glob
        
class MenuFile(QtGui.QMenu):
    def __init__(self, parent, widget):
        super(MenuFile, self).__init__(parent)        
        self.quit = QtGui.QAction(widget)
        self.quit.setText('quit')
        self.quit.triggered.connect(self._quit)
        self.addAction(self.quit)

    def _quit(self):
        guidata.qapplication().quit()

class MenuDanger(QtGui.QMenu):
    def __init__(self, parent, widget):
        super(MenuDanger, self).__init__(parent)
        
        self.clear_database = QtGui.QAction(widget)
        self.clear_database.setText('clear curvestore database...')
        self.clear_database.triggered.connect(clear_db)
        self.addAction(self.clear_database)
        
        self.sync_database = QtGui.QAction(widget)
        self.sync_database.setText('sync database')
        self.sync_database.triggered.connect(sync_db)
        self.addAction(self.sync_database)        
                
        
        self.reset_database = QtGui.QAction(widget)
        self.reset_database.setText('reset curvestore database...')
        self.reset_database.triggered.connect(self.do_reset_curvestore_db)
        self.addAction(self.reset_database)

        self.import_h5_files = QtGui.QAction(widget)
        self.import_h5_files.setText('import h5 files (already in place)...')
        self.import_h5_files.triggered.connect(self.import_h5_files_frominternal)
        self.addAction(self.import_h5_files)

        self.update_all_files = QtGui.QAction(widget)
        self.update_all_files.setText('update all files...')
        self.update_all_files.triggered.connect(self.do_update_all_files)
        self.addAction(self.update_all_files)
        
        self.dlbackup = QtGui.QAction(widget)
        self.dlbackup.setText('backup datalogger...')
        self.dlbackup.triggered.connect(self._dlbackup)
        self.addAction(self.dlbackup)

        self.dlrecover = QtGui.QAction(widget)
        self.dlrecover.setText('recover datalogger information from backup...')
        self.dlrecover.triggered.connect(self._dlrecover)
        self.addAction(self.dlrecover)
    
    def _dlrecover(self):
        datalogger_recovery()
        
    def _dlbackup(self):
        datalogger_backup()
    
    def do_update_all_files(self):
        update_all_files()
        
    def import_h5_files_frominternal(self):
        import_h5_files(inplace=True)
     
    def do_reset_curvestore_db(self):
        reset_db()    
        
    
        
class MenuDB(QtGui.QMenu):
    import_done = QtCore.pyqtSignal()
    def __init__(self, parent, widget):
        super(MenuDB, self).__init__(parent)
        
        self.forget_database_location = QtGui.QAction(widget)
        self.forget_database_location.setText('forget database location...')
        self.forget_database_location.triggered.connect(self.do_forget_db_location)
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
        self.import_h5_files.triggered.connect(self.import_h5_files_fromexternal)
        self.addAction(self.import_h5_files)

        self.import_oldformat_h5_files = QtGui.QAction(widget)
        self.import_oldformat_h5_files.setText('import h5 files in old format (no full data recovery)...')
        self.import_oldformat_h5_files.triggered.connect(self._import_oldformat_h5_files)
        self.addAction(self.import_oldformat_h5_files)
        
    
    def _backup_all_files(self):
        filename = str(QtGui.QFileDialog.getSaveFileName(parent=self))
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


            
    def import_h5_files_fromexternal(self):
        import_h5_files(inplace=False)


    

    def _import_oldformat_h5_files(self):
        """
        Import all .h5 files from a directory and subdirectories.
        """
        dirname = str(QtGui.QFileDialog.getExistingDirectory(parent=self))
        if not dirname:
            return
        
        def archive_dir(added_ids, dirname, files):
            allanswers = -2
            for filename in files:
                fname = os.path.join(dirname, filename)
                if os.path.isfile(fname):
                    if fname.endswith('.h5'):
                        cur = curve.load_oldformat(fname)
                        cur_db = models.curve_db_from_curve(cur)
                        id = int(cur.params['id'])
                        try:
                            old_one = models.CurveDB.objects.get(id=id)
                        except ObjectDoesNotExist:
                            cur_db.id = cur.params['id']
                            cur_db.save()
                        else:
                            message = "A curve with the id " + str(id) + \
                            " already exists in your database." + "\n What should we do with curve " + \
                            cur.params["name"] + " ?"
                            if allanswers <= -1:
                                answer = QtGui.QMessageBox.question(self, 'existing id', message, 'forget about it', 'overwrite ' + old_one.params['name'], "use new id")
                                if allanswers == -2:
                                    secanswer = QtGui.QMessageBox.question(self, 'repeat', "Remember choice for future id conflicts?", 'Yes', 'No','Ask again')
                                    if secanswer == 0:
                                        allanswers = answer
                                    elif secanswer == 1:
                                        allanswers = -1
                                    elif secanswer == 2:
                                        allanswers = -2
                            else:
                                answer = allanswers
                            if answer==0:
                                continue
                            if answer==1:
                                cur_db.id = cur.params['id']
                                cur_db.save()
                            if answer==2:
                                cur_db.save()
                        added_ids.append(cur_db.id)

        added_ids = list()
        os.path.walk(dirname, archive_dir, added_ids)

        #loop over all added ids to confirm that everything is set properly
        for id in added_ids:
            c = models.CurveDB.objects.get(id=id)
            #if 'date' in c.params:
            #    c.date = c.params['date']
            if 'parent_id' in c.params:
                if not c.params['parent_id']==0:
                    parent = None
                    try:
                        parent = models.CurveDB.objects.get(pk=c.params['parent_id'])
                    except ObjectDoesNotExist:
                        print "Parent id "+str(c.params['parent_id'])+\
                        " of curve with id "+str(id)+" does not exist. Orphan created!"
                    else:
                        parent.add_child(c)
                    c.save()
            c.tags.append('oldformat/reimported')    
        print "Added the following ids:"
        print added_ids
        self.import_done.emit()

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
        
    def do_forget_db_location(self):
        forget_db_location()
    
class CurveEditorMenuBar(QtGui.QMenuBar):
    import_done = QtCore.pyqtSignal() 
    def __init__(self, parent):
        super(CurveEditorMenuBar, self).__init__(parent)
        self.menu_file_action = QtGui.QAction('file', parent)
        self.menu_file = MenuFile(self, parent)
        self.menu_file_action.setMenu(self.menu_file)
        
        self.menu_db_action = QtGui.QAction('database', parent)
        self.menu_db = MenuDB(self, parent)
        self.menu_db.import_done.connect(self.import_done)
        self.menu_db_action.setMenu(self.menu_db)
        
        self.menu_danger_action = QtGui.QAction('danger', parent)
        self.menu_danger = MenuDanger(self, parent)
        #self.menu_danger.import_done.connect(self.import_done)
        self.menu_danger_action.setMenu(self.menu_danger)
        
        self.addAction(self.menu_file_action)
        self.addAction(self.menu_db_action)
        self.addAction(self.menu_danger_action)

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