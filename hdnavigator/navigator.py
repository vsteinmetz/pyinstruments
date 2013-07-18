from conf_xml import conf,default_file
import os
import datetime
import re
import shutil

file_prefix ='\A[0-9]{4}_'
date_prefix = '\A20\d{2}-[0-1][0-9]-[0-3]\d_'  #beware of the bug of the year 2100
prefix_re = re.compile(file_prefix)
date_prefix_re = re.compile(date_prefix)

def get_last(names):
    """given a list of names e.g. ["0001_file1","0005_file2"], returns the largest prefix number"""
    nums = {}
    for i in names:
        n = prefix_re.match(i)
        if n is not None:
            n = n.group()[:-1]
            nums[int(n)] = i
    if len(nums) > 0:
        return nums[max(nums.keys())]
    

def get_num(names):
    nums = []
    for i in names:
        n = prefix_re.match(i)
        if n is not None:
            n = n.group()[:-1]
            nums.append(int(n))
    if len(nums) > 0:
        return max(nums)
    else:
        return 0


def get_immediate_subdirectories(dir):
    """returns only the directory names in the directory dir"""
    return [name for name in os.listdir(dir)
            if os.path.isdir(os.path.join(dir, name)) and prefix_re.match(name) is not None]

def remember_last(l,dirname,fnames):
    """remembers the last directory in the recursive walk and stores it in l[0]"""
    to_remove = [] # OK, there HAS to be a simpler way to do that but I didn't find it
    for n in fnames:
        if (not prefix_re.match(n)) and (not date_prefix_re.match(n)):
            to_remove.append(n)
    for i in to_remove:
        fnames.remove(i)
            
    #if prefix_re.match(os.path.split(dirname)[-1]) is not None:
    l[0] = dirname


def lower_last(dir):
    """gives the lower and last directory in an alphabetical way (excludes files and directories that don't have the correct prefix)"""
    l = [None,]
    os.path.walk(dir,remember_last,l)
    if l[0] == None:
        raise ValueError("defaultPath doesn't exist, you should create it, or define the variable HDnavigator.conf.defaultPath")
    dir = os.listdir(l[0])
    if len(dir)>0:
        return path.join(l[0],dir[-1])
    else:
        return l[0]

def next_number(path):
    """gives the next number to be added in the path"""
    num = get_num(os.listdir(path))
    return num+1


def is_there_same_date(names):
    nums = {}
    for i in names:
        n = date_prefix_re.match(i)
        if n is not None:
            n = n.group()[:-1]
            if n == str(datetime.date.today()):
                return True
    return False

##================================================
##  Objects contained in Navigator
##================================================


class Make(object):
    def __init__(self,parent):
        self._parent = parent   
    ##=============================
    ##    dir
    ##=============================    
    def dir(self,name = None):
        """makes a new directory, uses default.dir if no name provided."""
        if name is not None:
            self._parent.Default.dir = name
        np = self._parent.Next.dir
        if np == None:
            raise ValueError("Trying to write above the root directory")
        os.mkdir(np)
        self._parent.Go.move(np)
    
    ##=============================
    ##    sub directory
    ##=============================
    def sub_dir(self,name = None):
        """makes a new directory inside the current one, uses default.dir if no name provided."""
        if name is not None:
            self._parent.Default.dir = name
        np = self._parent.Next.sub_dir
        os.mkdir(np)
        self._parent.Go.move(np)
        
    ##=============================
    ##    sub directory
    ##=============================
    def today_dir(self,name = None):
        """makes a new directory inside the current one, uses default.dir if no name provided
        and appending as a prefix today's date"""
        if name is not None:
            self._parent.Default.dir = name
        dir = self._parent.Current.dir
        np = self._parent.Next.today_dir
        if is_there_same_date(os.listdir(dir)):
            raise ValueError("There is already a directory with the same date in " + dir)
        os.mkdir(np)
        self._parent.Go.move(np)
        
class Current(object):
    def __init__(self,parent):
        self._parent = parent   
    
    @property
    def _conf(self):
        return self._parent._conf
    ##=============================
    ##    dir
    ##=============================    
    @property
    def dir(self):
        """returns the current directory."""
        return self._conf.current.dir
    @dir.setter
    def dir(self,val):
        """changes the current directory."""
        self._conf.current.dir = val
        self._conf.serialize()
        return val
    
    @property
    def file(self):
        dir = self._parent.Current.dir
        return os.path.join(dir,"%04i"%(get_num(os.listdir(dir))) + "_" + self.Default.file)

class Default(object):
    def __init__(self,parent):
        self._parent = parent
        
    @property
    def _conf(self):
        return self._parent._conf
    ##=============================
    ##    default dir name
    ##=============================
    @property
    def dir(self):
        return self._conf.default.dir
    @dir.setter
    def dir(self,val):
        self._conf.default.dir = val
        self._conf.serialize()
        return val
    ##=============================
    ##    default_file_name
    ##=============================
    @property
    def file(self):
        return self._conf.default.file
    @file.setter
    def file(self,val):
        self._conf.default.file = val
        self._conf.serialize()
        return val
    
    ##=============================
    ##    root_path
    ##=============================
    @property
    def root_path(self):
        return self._conf.current.root_path
    @root_path.setter
    def root_path(self,val):
        self._conf.current.root_path = val
        self._conf.serialize()
        return val

class Go(object):
    def __init__(self,parent):
        self._parent = parent
        
    def move(self,dir):
        os.chdir(dir)
        self._parent.Current.dir = os.path.abspath(".")
        print self._parent.Current.dir
        
    @property
    def _conf(self):
        return self._parent._conf
        
    def up(self):
        if os.path.normcase(self._parent.Current.dir) == os.path.normcase(self._parent.Default.root_path):
            raise ValueError("Trying to go above the root directory")
        self.move(os.path.split(self._parent.Current.dir)[0])
    
    def down(self):
        """moves to the directory just below that's last by prefix order"""
        last_just_below = get_last(get_immediate_subdirectories(self._parent.Current.dir))
        if last_just_below == None:
            raise ValueError("No directory with prefix in "  + self._parent.Current.dir)
        self.move(last_just_below)
    
    def root_path(self):
        self.move(self._parent.Default.root_path)
        
    def last_below(self):
        dir = lower_last(self._parent.Current.dir)
        self.move(dir)
        
    def _current(self):
        """this function is hidden because current should always be the actual position"""
        try:
            self.move(self._parent.Current.dir)
        except WindowsError:
            print "could not move to the current location:\n" + self._parent.Current.dir + \
"""
Please, set correct default values e.g.:

nav.Default.root_path = "Z:/Data"
nav.Go.root_path()

For now, I will try to go to the root_path, and the last_below"""
            try:
                self.root_path()
            except WindowsError:
                self._parent.Default.root_path = \
                        os.path.abspath(os.curdir)
                self.root_path()
            else:
                self.last_below()
            
            
class Next(object):
    def __init__(self,parent):
        self._parent = parent
        
    @property
    def _conf(self):
        return self._parent._conf
    
    
    @property
    def file(self):
        return self._parent.next_file
    
    @property
    def sub_dir(self):
        dir = self._parent.Current.dir
        np = os.path.join(dir,"%04i"%next_number(dir) + "_" + self._parent.Default.dir)  
        return np
    
    @property
    def dir(self):
        if os.path.normcase(self._parent.Current.dir) == os.path.normcase(self._parent.Default.root_path):
            return None
        dir = os.path.split(self._parent.Current.dir)[0]
        np = os.path.join(dir,"%04i"%next_number(dir) + "_" + self._parent.Default.dir)
        return np
    
    @property
    def today_dir(self):
        dir = self._parent.Current.dir
        todayStr = str(datetime.date.today())
        np = os.path.join(dir,todayStr + "_" + self._parent.Default.dir)
        return np
    
    
class Navigator(object):
    def __init__(self):
        self._conf = conf(default_file(__file__))
        try:
            self._values = self._conf.values
        except AttributeError:
#            self._values = self._conf.sub("values",root_path = "C:/Data")
            self._default = self._conf.sub("default",dir = "new_dir",file = "new_file")
            self._current = self._conf.sub("current",root_path = "C:",dir = "C:",file = "new_file")
            self._conf.serialize()
        self.Default = Default(self)
        self.Make = Make(self)
        self.Current = Current(self)
        self.Go = Go(self)
        self.Next = Next(self)
        
        self.Go._current()
    
    @property
    def next_file(self,ext = ".h5"):
        def_file = self.Default.file
        if def_file[-3:]!=ext:
            def_file = def_file+ext
        dir = self.Current.dir
        return os.path.join(dir,"%04i"%(get_num(os.listdir(dir))+1) + "_" + def_file)
    
    
