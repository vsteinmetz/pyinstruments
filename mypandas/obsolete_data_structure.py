@monkey_add(pandas.DataFrame)
@monkey_add(pandas.Series)
def get_data(self):
    return self



@monkey_add(pandas.DataFrame)
@monkey_add(pandas.Series)
def customize(self,d):
    """customize a Series by monkey adding all usefull metadata"""
    recurse_through_dict(self,"meta",d)
    

def recurse_through_meta(meta,name = "custom",d = dict()):
    if isinstance(meta,basestring) or isinstance(meta,bool) or isinstance(meta,numbers.Number):
        d[name] = meta
        return d
    ### else, recurse further
    d[name] = dict()
    for i in dir(meta):
       if i[0] != "_": 
           recurse_through_meta(getattr(meta,i),i,d[name])
    return d
         
         
def recurse_through_dict(custom,name,d):
    if isinstance(d,basestring) or isinstance(d,bool) or isinstance(d,numbers.Number):
        setattr(custom,name,d)
        return custom
    if not isinstance(d,dict):
        print "loosing some parameters: value is neither a dictionnary, nor a string or number or boolean: " + name 
        return
    setattr(custom,name,MetaData())
    at = getattr(custom,name)
    for k in d.keys():
        recurse_through_dict(at,k,d[k])
    return custom





@monkey_add(pandas.Series)
def upgrade(self):
    return Series(self)

@monkey_add(pandas.DataFrame)
def upgrade(self):
    return DataFrame(self)

class My_Base_Data(object):
    def __gt__(self,b):
        if isinstance(b,self.__class__):
            return self.data > b.data
        return self.data > b
    
    def __ge__(self,b):
        if isinstance(b,self.__class__):
            return self.data >= b.data
        return self.data >= b
    
    
    def __lt__(self,b):
        if isinstance(b,self.__class__):
            return self.data < b.data
        return self.data < b
    
    def __le__(self,b):
        if isinstance(b,self.__class__):
            return self.data <= b.data
        return self.data <= b
    
    def __eq__(self,b):
        if isinstance(b,self.__class__):
            return self.data == b.data
        return self.data == b
    
    def __neq__(self,b):
        if isinstance(b,self.__class__):
            return self.data != b.data
        return self.data != b
    
    def __add__(self,b):
        if isinstance(b,self.__class__):
            return self.__class__(self.data + b.data)
        return self.__class__(b + self.data)

    def __radd__(self,b):
        if isinstance(b,self.__class__):
            return self.__class__(self.data + b.data)
        return self.__class__(b + self.data)    
    
    def __sub__(self,b):
        if isinstance(b,self.__class__):
            return self.__class__(self.data - b.data)
        return self.__class__(self.data - b)
    
    def __rsub__(self,b):
        if isinstance(b,self.__class__):
            return self.__class__(b.data - self.data)
        return self.__class__(b - self.data)
    
    def __neg__(self):
        return self.__class__(- self.data)
    
    def __pow__(self,b):
        if isinstance(b,self.__class__):
            return self.__class__(self.data**b.data)
        return self.__class__(self.data**b)
    
    def __mul__(self,b):
        if isinstance(b,self.__class__):
            self.__class__(b.data*self.data)
        return self.__class__(b*self.data)
    
    def __rmul__(self,b):
        if isinstance(b,self.__class__):
            self.__class__(b.data*self.data)
        return self.__class__(b*self.data)
    
    def __div__(self,b):
        if isinstance(b,self.__class__):
            return self.__class__(self.data/b.data)
        return self.__class__(self.data/b)
    
    def __rdiv__(self,b):
        if isinstance(b,self.__class__):
            return self.__class__(b.data/self.data)
        return self.__class__(b/self.data)
    
    @property
    def index(self):
        return self.data.index

    @index.setter
    def index(self, index):
        self.data.index = index
    
    @property
    def value(self):
        return self.data.value

    @value.setter
    def value(self, value):
        self.data.value = value        
    
    
    def save(self,file = None):
        from pandas import HDFStore
        if(file[-3:]!=".h5"):
            file = file + ".h5"
        
        if hasattr(self,"meta"):
            f = h5py.File(file)
            meta_on_file = f.create_group('meta')
            if isinstance(self.meta,dict):
                for k,v in self.meta.iteritems():
                    v.save(meta_on_file.create_group(k))
            else:
                self.meta.save(meta_on_file)
        f.close()
        f = HDFStore(file)
        f["data"] = self.data
        f.close()


class Series(My_Base_Data):
    def __init__(self,data = None,meta = None,*args,**kwds):
        """see pandas.Series for help"""
        self.data = pandas.Series(data,*args,**kwds)
        self.format_name()
        if meta is None:
            self.meta = MetaData()
        else:
            self.meta = meta
            
    
    def __getitem__(self,i):
        s = self.data.__getitem__(i)
        if isscalar(s):
            return s
        return Series(s,meta = self.meta)
        
    def format_name(self):
        if self.name is not None:
            self.name = format_name(self.name)
        

    def dummy(self):
        print "dummy"

#    def set_meta(self,*args,**kwds):
#        """use propname = propvalue to set a value, and"""
#        for i in args:
#            setattrr(self.meta,i,MetaData())
#        
#        for k,v in kwds.iteritems():
#            setattr(self.meta,k,v)
    
    @property
    def real(self):
        return self.data.real
    
    @property
    def imag(self):
        return self.data.imag
        
    @property
    def name(self):
        try:
            return self.data.name
        except AttributeError:
            return None
    @name.setter
    def name(self, value):
        self.data.name = value
        
    def set_meta_from_dict(self,d):
        recurse_through_dict(self.meta,"meta",d)
        
        
class DataFrame(My_Base_Data):
    def __setitem__(self,key,val):
        self.data[key] = val.get_data()  #### overload the function __setitem__ of pandas.DataFrame rather than this
        self._grab_meta(val,name = key)
    
    def __delitem__(self,it):
        del self.data[it]
        del self.meta[it]
    
    def __getitem__(self,i):
        to_ret = self.data[i]
        if isinstance(to_ret,pandas.DataFrame):
            res = DataFrame(to_ret)
            for c in to_ret.columns:
                if c in self.meta:
                    res.meta[c] = self.get_meta(c)
            return res
        if isinstance(to_ret,pandas.Series):
            res = Series(to_ret)
            if hasattr(res,"name"):
                if res.name in self.meta:
                    res.meta = self.get_meta(format_name(res.name))
            return res
        return to_ret
    
    def __delitem__(self,i):
        del self.data[i]
        if i in self.meta:
            del self.meta[i]
    
    def __init__(self,data=None,meta = None,*args,**kwds):
        """see pandas.DataFrame for help"""
        if isinstance(data,pandas.DataFrame):
            data = data.rename(columns = format_name)
        if meta is None:
            meta = dict()
        self.meta = meta
        build = False
        if isinstance(data,DataFrame):
            self.data = data.data
            self.meta = data.meta
            return
        
        if isinstance(data,dict):
            for k,v in data.iteritems():
                if isinstance(v,Series):
                    build = True
        if build:
            self.data = pandas.DataFrame()
            for k,col in data.iteritems():
                col.name = k
                self.join(col)
        else:
            self.data = pandas.DataFrame(data,*args,**kwds)
            #for i in self.data.columns:
                #self.meta[format_name(i)] = MetaData()
        
    def add_labeled_df(self,df,name):
        df.columns = pandas.MultiIndex.from_tuples(zip([name]*len(df.columns),df.columns))
        if self.empty:
            self.data = pandas.concat([df.data,self.data],axis = 1)
        else:
            self.data = pandas.concat([self.data,df.data],axis = 1)
    @property
    def empty(self):
        return self.data.empty
        
    def get_meta(self,i,default = MetaData()):
        if i in self.meta:
            return self.meta[i]
        else:
            return default

    def _grab_meta_from_series(self,other,name = None):
        try:
            if other.meta is None:
                meta = MetaData()
            else:
                meta = other.meta
        except AttributeError:
            meta = MetaData()
        if name == None:
            name = other.name
        self.meta[format_name(name)] = meta

    def _grab_meta(self,other,name = None):
        if isinstance(other,Series):
            self._grab_meta_from_series(other,name)
            return
        if isinstance(other, DataFrame):
            for i in other.columns:
                self._grab_meta_from_series(other[i])
            return
        if isinstance(other, pandas.DataFrame):
            for i in other.columns:
                self.meta[format_name(i)] = MetaData()
            return
        self.meta[format_name(other.name)] = MetaData()
            
    def join(self,other,how = 'outer',**kwds):
        """either creates a new dataFrame containing only column s, or appends it at the end
        see pandas.DataFrame.join for help"""
        if self.data.empty:
            self.data = pandas.DataFrame({other.name:other.get_data()})
        else:
            self.data = self.data.join(other.get_data(),how = how,**kwds)

        self._grab_meta(other)
        return self
    
    
    #def save_meta(self,filename):
    #    if hasattr(self,"meta"):
    #        self
#   #             f["meta_"+k] = pandas.Series(recurse_through_meta(v))
                
    def save_data(self,f):
        f["data"] = self.data
        
    def save_to_store(self,f):
        self.save_meta_to_store(f)
        self.save_data_to_store(f)
        
        
    def saveAsh5(self,file = None):
        from pandas import HDFStore
        if file[-3:]!=".h5":
            file = file + ".h5"
        f = HDFStore(file,"w")
        self.save_to_store(f)
        f.close()
    
    @property
    def columns(self):
        return self.data.columns

    @columns.setter
    def columns(self,col):
        self.data.columns = col
    
    def set_meta_from_dict(self,colname,d):
        dummy = MetaData()
        recurse_through_dict(dummy,"meta",d)
        self.meta[colname] = dummy.meta.custom
        
        
        
def register_func(f):
    def function(self,*args,**kwds):
        return f(self.data,*args,**kwds)
    return function

def monkey_inherit(child,parent,funcs):
    for func in funcs:
        f = getattr(parent,func)
        function = register_func(f)
        setattr(child,func,function)
        
common = ["plot","ix","keys","std","head"]
monkey_inherit(Series,pandas.Series,common + ["__getslice__","mean"])        
monkey_inherit(DataFrame,pandas.DataFrame,common + ["transpose"])        
    
@monkey_add(Series)
@monkey_add(DataFrame)
def get_data(self):
    return self.data


@monkey_add(Series)
@monkey_add(DataFrame)
def __repr__(self):
    return "my_data_structure\n" + self.data.__repr__()

