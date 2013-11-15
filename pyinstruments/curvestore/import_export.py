from pyinstruments.datastore.settings import MEDIA_ROOT, DATABASE_FILE
from pyinstruments.curvestore import models
from curve import Curve
import subprocess

from django.db import reset_queries
from django.core.exceptions import ObjectDoesNotExist
from PyQt4 import QtCore, QtGui
import os.path
import os

def update_all_files():
        res = QtGui.QMessageBox.question(QtGui.QWidget(),
                                           "are you sure",
                                           "It's strongly advised to backup the directory " \
                                           + MEDIA_ROOT \
                                           + " before updating the files. Proceed anyway ?",
                                           "Cancel",
                                           "OK")
        if res==0:
            return
        allcurves = models.CurveDB.objects.all()
        total = len(allcurves)
        n_done = 0
        for cur in allcurves:
            #cur.data
            
            cur.params
            file = cur.get_full_filename()
            directo = os.path.dirname(file)
            if not os.path.exists(directo):
                os.makedirs(directo)
            Curve.save(cur, file, with_data=False)
            n_done += 1
            print 'updated ' + str(n_done) + ' curves / ' + str(total) 
            #del cur._data
            #gc.collect()

        print "All "+str(len(allcurves))+" curve files are now up to date! "

class CustomMessageBox(QtGui.QMessageBox):
    def __init__(self, message):
        super(CustomMessageBox, self).__init__()
        self.setText(message)
        self.addButton('drop new curve', 1)
        self.addButton('overwrite old curve', 2)
        self.addButton('use new id', 3)
        self.addButton('abort import now', 4)
        self.checkbox = QtGui.QCheckBox()
        #self.form = QtGui.QFormLayout()
        self.label = QtGui.QLabel('Apply the same choice for future id conflict')
        #self.form.addRow(self.checkbox, self.label)
        self.layout().addWidget(self.checkbox)
        self.layout().addWidget(self.label)
    
    def ask(self):
        res = self.exec_()
        dic = {1:'overwrite', 2:'new_id',0:'drop', 3:'abort'}
        return (self.checkbox.checkState()==2, dic[res])

def import_h5_files(inplace=False):
        """
        Import all .h5 files from a directory and subdirectories.
        """
        
        threshold_garbage = 100
        askagain = True
        while askagain:
            dirname = str(QtGui.QFileDialog.getExistingDirectory())
            if not dirname:
                return
            if inplace:    
                askagain = os.path.commonprefix([os.path.abspath(dirname),
                                                 os.path.abspath(MEDIA_ROOT)]) \
                                            !=os.path.abspath(MEDIA_ROOT)
                if askagain:
                    QtGui.QMessageBox.information(QtGui.QWidget(), 'wrong directory', 'please, choose a directory in ' + MEDIA_ROOT)
            else:
                askagain = False
        idpolitics=None
    
    
    
        
    
   #     def archive_dir(files_info, dirname, files):

                        #self.progress_bar.update((len(added_ids)*100)/total_files)
        added_childs = list()
        
        total_files = 0
        for root, dirs, files in os.walk(dirname):
            total_files+=len(files)

        total_added = 0
        answer=None
        index = 0
        for root, dirs, files in os.walk(dirname):
            for filename in files:
                index+=1
                if index>threshold_garbage:
                    print 'freeing up memory'
                    reset_queries()
                    index = 0
                    
                fname = os.path.join(root, filename)
                if os.path.isfile(fname):
                    if fname.endswith('.h5'):
                        try: 
                            cur_db = models.curve_db_from_file(fname,inplace=inplace,overwrite=idpolitics)
                        except models.IdError as e:
                            if not answer:
                                message = str(e)
                                #message_box = QtGui.QMessageBox()
                                message_box = CustomMessageBox(message)
                                (applies_to_all, answer) = message_box.ask()
                                this_answer = answer
                                if not applies_to_all:
                                    answer = None
#                           answer = message_box.question(QtGui.QWidget(), 'existing id', message, 'forget about it', 'overwrite ', "use new id")
                            if this_answer=="drop":
                                continue
                            if this_answer=="overwrite":
                                cur_db = models.curve_db_from_file(fname,inplace=inplace,overwrite=True)
                            if this_answer=="new_id":
                                cur_db = models.curve_db_from_file(fname,inplace=inplace,overwrite=False)
                            if this_answer=="abort":
                                return

                        cur_db.save()
                        total_added += 1
                        if 'parent_id' in cur_db.params:
                            if cur_db.params['parent_id']!=0:
                                added_childs.append(cur_db.id)
                        print "imported " + str(total_added) + '/' + str(total_files)
      
      
        #self.progress_bar.show()
      #  os.path.walk(dirname, archive_dir, [added_ids, total_files, inplace, idpolitics])
        #self.progress_bar.hide()
        #loop over all added ids to confirm that everything is set properly

        from pyinstruments.curvestore.models import model_monitor
        model_monitor.blockSignals(True)
        index = 0
        print 'I will now add a child-parent relationship to ' + str(len(added_childs)) + ' curves'
        total_childs_added = 0
        tot = len(added_childs)
        for id in added_childs:
            c = models.CurveDB.objects.get(id=id)
            index+=1
            if index>threshold_garbage:
                print 'freeing up memory'
                reset_queries()
                index = 0
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
                    total_childs_added += 1
                    print str(total_childs_added) + '/' + str(tot) + ' childs appended'
        model_monitor.blockSignals(False)        
        #print "Added the following ids:"
        #print total_added
        #self.import_done.emit()

def clear_db():
    res = QtGui.QMessageBox.question(QtGui.QWidget(),
                                           "are you sure",
                                           "It's strongly advised to backup the file " \
                                           + DATABASE_FILE \
                                           + " before resetting the database. Careful, this command leaves all files in place, if you plan on using import files in place to recover the database, please, make sure they have been updated first.",
                                           "Cancel",
                                           "OK")
    if res:
        manage_file = os.path.dirname(__file__) + '/../manage.py'
        sql_command = subprocess.check_output(["python", manage_file, 'sqlclear', 'curvestore'])
        subprocess.call(['sqlite3', DATABASE_FILE, sql_command])
    return res
      
def sync_db():
    manage_file = os.path.dirname(__file__) + '/../manage.py'
    subprocess.call(["python", manage_file, 'syncdb'])

def reset_db():
    if clear_db():
        sync_db()
    
    
def cleanup_directory():
    db_files = []
    dir_files = []
    to_remove = []
    
    for curve in models.CurveDB.objects.all():
        db_files.append(os.path.abspath(os.path.join(MEDIA_ROOT, curve.data_file.name)))
    print 'found ' + str(len(db_files)) + ' curves in the db...'
    
    for root, dirs, files in os.walk(MEDIA_ROOT):
        for f in files:
            if f.endswith('.h5'):
                dir_files.append(os.path.abspath(os.path.join(root, f)))
    
    print 'found ' + str(len(dir_files)) + ' h5 files in the directory...'
       
    dir_files.sort()
    db_files.sort() 
    index_db = 0
    index_dir = 0
    tot = len(db_files)
    while(index_db<tot):
        db = db_files[index_db]
        dir = dir_files[index_dir]
        if db==dir:
            index_db+=1
            index_dir+=1
        else:
            to_remove.append(dir)
            index_dir+=1
       
    print to_remove
    
    
    if QtGui.QMessageBox.question(QtGui.QWidget(),
                                  'Are you sure?',
                                'Found ' + str(len(to_remove)) + ' h5 files in the directory ' + MEDIA_ROOT + ' without entry in the database. Are you sure you want to delete them ?',
                               'Cancel',
                               'OK'):
        for f in to_remove:
            os.remove(f)
def forget_db_location():
    settings = QtCore.QSettings('pyinstruments', 'pyinstruments')
    settings.setValue('database_file', "")
    QtGui.QMessageBox.information(QtGui.QWidget(),
                                             'change-database',
                                             'change will take effect at the next startup')

