from pyinstruments.datastore.settings import MEDIA_ROOT, DATABASE_FILE
from pyinstruments.curvestore import models
from curve import Curve
import subprocess

from PyQt4 import QtCore, QtGui
import os.path
import glob

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
    
        def archive_dir(files_info, dirname, files):
            [added_ids, total_files,inplace,idpolitics] = files_info
            answer=None
            for filename in files:
                print "imported " + str(len(added_ids)) + '/' + str(total_files)
                fname = os.path.join(dirname, filename)
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
                        added_ids.append(cur_db.id)
                        #self.progress_bar.update((len(added_ids)*100)/total_files)
        added_ids = list()
        total_files = len(glob.glob(dirname + '/*/*/*/*.h5'))
      
        #self.progress_bar.show()
        os.path.walk(dirname, archive_dir, [added_ids, total_files, inplace, idpolitics])
        #self.progress_bar.hide()
        
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
                
        print "Added the following ids:"
        print added_ids
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
    
    
        
        

def forget_db_location():
    settings = QtCore.QSettings('pyinstruments', 'pyinstruments')
    settings.setValue('database_file', "")
    QtGui.QMessageBox.information(QtGui.QWidget(),
                                             'change-database',
                                             'change will take effect at the next startup')

