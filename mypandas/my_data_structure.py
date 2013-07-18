import pandas
import numbers
import h5py
from numpy import iterable,isscalar
from pandas import Series,DataFrame,HDFStore
from h5py import File

def monkey_add(cls):
    """use this as decorator (@monkey_add) before a function to add ot to all pandas.Series instances"""
    def monkey_add_to_class(func):
        setattr(cls,func.__name__,func)
        return func
    return monkey_add_to_class

#################################################################
### redefine the __init__ function for Series                 ###
#################################################################
__init_series_old__ = Series.__init__

def __init__(self, data=None, index=None, dtype=None, name=None, copy=False):
    __init_series_old__(self,data, index, dtype, name, copy)
    if name is None:
        self.name = "no_name"
    self.replace_name_by_meta_index()
        
__init__.__doc__ = pandas.Series.__init__.__doc__
monkey_add(pandas.Series)(__init__)

#################################################################
### redefine the __init__ function for DataFrame              ###
#################################################################
__init_df_old__ = DataFrame.__init__
def __init__(self, data=None, index=None, columns=None, dtype=None, copy=False):
    if isinstance(data,dict):
        newdata = dict()
        for k,s in data.iteritems():
            if isinstance(s,Series):
                if s.meta is not None:
                    newindex = MetaIndex(k)
                    newindex.meta = s.meta
                    newdata[newindex] = s
                else:
                    newdata[k] = s
            else:
                newdata[k] = s
        data = newdata
    __init_df_old__(self, data, index, columns, dtype, copy)

__init__.__doc__ = pandas.DataFrame.__init__.__doc__
monkey_add(pandas.DataFrame)(__init__)


__setitem_old__ = pandas.DataFrame.__setitem__
def __setitem__(self,key,value):
    if isinstance(value,Series):
        if isinstance(key,basestring):
            key = MetaIndex(key)
            key._meta = value.meta
    __setitem_old__(self,key,value)
    
__setitem__.__doc__ = pandas.DataFrame.__setitem__.__doc__
    
monkey_add(pandas.DataFrame)(__setitem__)



#@monkey_add(pandas.Series)
def set_name(self,val):
    """allows one to change the name of a Series without loosing the MetaData that are stored in the name object"""
    if isinstance(val,basestring):
        if hasattr(self,"_name") and isinstance(self._name,MetaIndex):
            temp = self._name._meta
            self._name = MetaIndex(val)
            self._name._meta = temp
        else:
            self._name = MetaIndex(val)

def get_name(self):
    try: 
        return self._name
    except AttributeError:
        return None


#pandas.Series.name = property(get_name,set_name)


@monkey_add(Series)
def replace_name_by_meta_index(self):
    #if isinstance(self.name,basestring):
    if self.meta == None:
        self.name = MetaIndex(self.name)
        
@monkey_add(Series)
def replace_meta_index_by_names(self):
    res = self.copy()
    if isinstance(self.name,MetaIndex):
        res.name = str(self.name)
    return res
    

def last_if_tuple(name):
    if isinstance(name,tuple):
        name = name[-1]
    else:
        name = name
    return name

def to_meta_index(name):
    if isinstance(name,tuple):
        name = list(name)
        if isinstance(name[-1],str):
            name[-1] = MetaIndex(name[-1])
    return name
    if isinstance(name,str):
        return MetaIndex(name)

@monkey_add(DataFrame)
def replace_names_by_meta_index(self):
    new_col = [to_meta_index(k) for k in self.columns]
    if isinstance(self.columns,pandas.MultiIndex):
        self.columns = pandas.MultiIndex.from_tuples(new_col)
    else:
        self.columns = new_col
    #for col in self.columns:
    #    s = self[col]
    #    s.replace_name_by_meta_index()
                
def meta_to_str(index):
    if isinstance(index,tuple):
        index = list(index)
        for i,v in enumerate(index):
            if isinstance(v,MetaIndex):
                index[i] = str(v)
    else:
        if isinstance(index,MetaIndex):
            index = str(index)
    return index
        

@monkey_add(DataFrame)
def replace_meta_index_by_names(self):
    res = self.copy()
    #for i,k in enumerate(res.columns):
    new_col = [meta_to_str(k) for k in res.columns]
    if isinstance(res.columns,pandas.MultiIndex):
        res.columns = pandas.MultiIndex.from_tuples(new_col)
    else:
        res.columns = new_col
    return res
            

def save_meta_to_file(obj,file):
    """appends the meta data of obj (Series or DataFrame) into a file designated with the filename file"""
    file = h5py.File(file)
    if isinstance(obj, Series):
        if obj.meta is not None:
            g = file.create_group("meta")
            obj.meta.save(g)
    if isinstance(obj, DataFrame):
        meta = file.create_group("meta")
        for col in obj.columns:
            s = obj[col]
            if s.meta is not None:
                g = meta.create_group(format_name(str(col)))
                s.meta.save(g)
    file.close()
##############################################
##     Load and Save
##############################################
def load(file,copy_first = False):
    if copy_first:
        import shutil
        import os
        temp = os.path.dirname(__file__) + "/temp.h5"
        shutil.copyfile(file,temp)
        file = temp
    f = HDFStore(file,"r")
    s = f["data"]
    f.close()
    
    f = File(file,'r')
    if isinstance(s,Series):
        s.meta.set(**f["meta"])
    if isinstance(s,DataFrame):
        s.replace_names_by_meta_index()
        for c in s.columns:
            col = s[c]
            if col.meta is not None:
                col.meta.set(**f["meta"][format_name(str(c))])
    f.close()
    #for k,v in .iteritems():
    #    s.meta.set(**f["meta"])
    #        s.set_meta_from_dict(k.lstrip("meta_"),dict(f[k]))
    #f.close()
    return s


@monkey_add(Series)
@monkey_add(DataFrame)
def save(self,file = None):
        from pandas import HDFStore
        if file[-3:]!=".h5":
            file = file + ".h5"
        f = HDFStore(file,"w")
        f["data"] = self.replace_meta_index_by_names()
        f.close()
        save_meta_to_file(self,file)





def get_meta(self):
    name = last_if_tuple(self.name)
    try:
        return name.meta
    except AttributeError:
        return None
    
def set_meta(self,meta):
    self.name.meta = meta

Series.meta = property(get_meta,set_meta)

def format_name(name):
    if isinstance(name,basestring):
        name = name.replace(" ","_")
    return name


class MetaData(dict):
    """a simple container class that also allows to browse the content by d.sub.sub..."""
    def __setitem__(self,k,val):
        k = format_name(k)
        dict.__setitem__(self,k,val)
        setattr(self,k,val)
        
    def __delitem__(self,k):
        dict.__delitem__(self,k)
        delattr(self,format_name(k))
        
    
    def set(self,*args,**kwds):
        """use set(propname = propvalue,...) to set a value, and set(node,...) to add a hierarchical node"""
        for i in args:
            self[i] = MetaData()
        
        for k,v in kwds.iteritems():
            if isinstance(v,h5py.Dataset):
                self[k] = v.value
                continue
            if iterable(v):
                self.set(k)
                self.get(k).set(**v)
            else:
                self[k] = v

    #def get(self,name):
    #    return getattr(self,format_name(name))

    def save(self,h5group):
        """saves the metadata tree to the h5group that is obtained using
        f = h5py.File(adress)
        h5group = f.create_group(name)"""
        for k,v in self.iteritems():
            if isinstance(v,MetaData):
                gr = h5group.create_group(k)
                v.save(gr)
            else:
                if isscalar(v):
                    h5group.create_dataset(k,data = v)
                else:
                    print "lost metadata "+ k + " not a scalar type"


class MetaIndex:
    """This class mimics a string and is intended to serve as the name of a Series or a DataFrame's column in order to
    contain the meta-data like RBW and so on..."""
    def __hash__(self):
        return self.str.__hash__()
    
    def __eq__(self,other):
        return self.str == str(other)
    
    #def __new__(cls,st):
    #    return str.__new__(cls,format_name(st))
    
    def __init__(self,st):
        #obj = str.__new__(cls,format_name(st))
        self.str = str(format_name(st))
        self._meta = MetaData()
        #return obj
    
    def __repr__(self):
        return self.str
    
    
    def __str__(self):
        return self.str
    
    def __unicode__(self):
        return unicode(self.str)
    
    @property
    def meta(self):
        return self._meta
    
    @meta.setter
    def meta(self,meta):
        self._meta = meta


