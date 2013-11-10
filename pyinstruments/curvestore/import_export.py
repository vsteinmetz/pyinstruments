from pyinstruments.datastore.settings import MEDIA_ROOT, DATABASE_FILE
from pyinstruments.curvestore import models
from curve import Curve
import subprocess

from PyQt4 import QtCore, QtGui
import os.path
import glob

def update_all_files():
        res = QtGui.QMessageBox().question(QtGui.QWidget(),
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

def import_h5_files(inplace=False):
        """
        Import all .h5 files from a directory and subdirectories.
        """
        
        dial = QtGui.QFileDialog()
        askagain = True
        while askagain:
            dirname = str(dial.getExistingDirectory())
            if not dirname:
                return
            if inplace:    
                askagain = os.path.commonprefix([os.path.abspath(dirname),
                                                 os.path.abspath(MEDIA_ROOT)]) \
                                            !=os.path.abspath(MEDIA_ROOT)
                if askagain:
                    mes = QtGui.QMessageBox()
                    mes.information(QtGui.QWidget(), 'wrong directory', 'please, choose a directory in ' + MEDIA_ROOT)
            else:
                askagain = False
        idpolitics=None
    
        def archive_dir(files_info, dirname, files):
            [added_ids, total_files,inplace,idpolitics] = files_info
            allanswers = -2
            for filename in files:
                print "imported " + str(len(added_ids)) + '/' + str(total_files)
                fname = os.path.join(dirname, filename)
                if os.path.isfile(fname):
                    if fname.endswith('.h5'):
                        try: 
                            cur_db = models.curve_db_from_file(fname,inplace=inplace,overwrite=idpolitics)
                        except models.IdError as e:
                            message = str(e)
                            message_box = QtGui.QMessageBox()
                            answer = message_box.question(QtGui.QWidget(), 'existing id', message, 'forget about it', 'overwrite ', "use new id")
                            if answer==0:
                                continue
                            elif answer==1:
                                cur_db = models.curve_db_from_file(fname,inplace=inplace,overwrite=True)
                            else:
                                cur_db = models.curve_db_from_file(fname,inplace=inplace,overwrite=False)
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
        
def reset_db():
    res = QtGui.QMessageBox().question(QtGui.QWidget(),
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
        subprocess.call(["python", manage_file, 'syncdb'])
        
def forget_db_location():
    settings = QtCore.QSettings('pyinstruments', 'pyinstruments')
    settings.setValue('database_file', "")
    dial = QtGui.QMessageBox.information(self,
                                             'change-database',
                                             'change will take effect at the next startup')

