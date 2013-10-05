import pandas
import h5py
import os
import numpy

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
        
    def __init__(self, data = None, meta = dict()):
        self._data = data
        self._metadata = MetaData(**meta)
        
        
    def plot(self, *args, **kwds):
        self.data.plot(*args, **kwds)
    
    plot.__doc__ = pandas.Series.plot.__doc__
    
    
    def save(self, filename, meta = True):
        with pandas.get_store(filename) as store:
            store["data"] = self._data
        
        with h5py.File(filename) as the_file:
            try:
                meta = the_file["meta"]
            except KeyError:
                meta = the_file.create_group("meta")
            for key, value in self.meta.iteritems():
                try: 
                    meta[key].write_direct(numpy.array(value))
                except KeyError:
                    meta.create_dataset(key, data = value)
    
    def load_data(self, filename):
        with pandas.get_store(filename, "r") as store:
            self._data = store["data"]
    
    @property
    def data(self):
        return self._data
    
    @property
    def meta(self):
        return self._metadata
        
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
    return Curve(data, meta = kwds)