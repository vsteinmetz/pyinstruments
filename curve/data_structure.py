import pandas
import h5py
import os

class MetaData(dict):
    """a container class for all the meta data associated to the curve
    e.g.: measurement Bandwidth ...
    """
    
    def __init__(self, **kwds):
        for key, value in kwds.iteritems():
            self[key] = value
    
    def __getattr__(self, attr):
        try:
            super(MetaData, self).__getattribute__(attr)
        except AttributeError:
            return self[attr]
    
    def __dir__(self):
        return self.keys()

class Curve(object):
    """a container class that contains:
    1) The data in pandas Series format (self.data)
    2) The metadata in self.meta as MetaData format (dict-like object) 
    """
    
    def __init__(self, data, **kwds):
        self.data = data
        self.meta = MetaData(**kwds)
        
    def plot(self, *args, **kwds):
        self.data.plot(*args, **kwds)
    
    plot.__doc__ = pandas.Series.plot.__doc__
    
    def save(self, filename, meta = True):
        with pandas.get_store(filename) as store:
            store["data"] = self.data
        
        with h5py.File(filename) as the_file:
            meta = the_file.create_group("meta")
            for key, value in self.meta.iteritems():
                meta.create_dataset(key, data = value)       
        
    def load_data(self, filename):
        with pandas.get_store(filename, "r") as store:
            self.data = store["data"]
        
        
def load(filename):
    """loads the curve at filename"""
    with pandas.get_store(filename, "r") as store:
            data = store["data"]
    kwds = dict()
    with h5py.File(filename) as the_file:
            try:
                meta = the_file["meta"]
            except KeyError:
                pass
            else:
                for key, value in meta.iteritems():
                    kwds[key] = value.value
    return Curve(data, **kwds)