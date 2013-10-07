import fitting

import pandas
import h5py
import os
import numpy
from datetime import datetime

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
    2) The parameters in self.meta as MetaData format (dict-like object) 
    """
        
    def __init__(self):
        self._params = None
        self._data = None
        self._tags = None
        
    def set_data(self, data):
        self._data = data
        
    def set_params(self, **kwds):
        if not self._params:
            self._params = MetaData()
        for key, val in kwds.iteritems():
            self._params[key] = val
        
    def plot(self, *args, **kwds):
        self.data.plot(*args, **kwds)
    
    plot.__doc__ = pandas.Series.plot.__doc__
    
    def save(self, filename):
        if self._data is None:
            raise ValueError("could not save curve, no data was set")
        if self._params is None:
            raise ValueError("could not save curve, no params were set")
        
        with pandas.get_store(filename) as store:
            store["data"] = self._data
        
        with h5py.File(filename) as the_file:
            try:
                params = the_file["params"]
            except KeyError:
                params = the_file.create_group("params")
            for key, value in self.params.iteritems():
                if isinstance(value, datetime):
                    value = value.strftime("%y/%m/%d/%H/%M/%S/%f")
                try:
                    params[key]
                except KeyError:  
                    params.create_dataset(key, data=value)
                else:
                    del params[key]
                    params.create_dataset(key, data=value)
                    
                    
    
    def load_data(self, filename):
        with pandas.get_store(filename, "r") as store:
            self._data = store["data"]

    def get_plottable_data(self):
        if self.params['curve_type']=='NaCurveComplex':
            return abs(self.data)**2
        else:
            return self.data
                       
    @property
    def data(self):
        return self._data
    
    @property
    def params(self):
        return self._params
        
    def fit(self, func, **kwds):
        """
        Makes a fit of the curve and returns the child fit curve
        """ 
        
        fit_curve = Curve()
        fitter = fitting.Fit(self.data, func, **kwds)
        fit_curve.set_data(fitter.fitdata)
        fit_curve.set_params(**fitter.getparams())
        fit_curve.params["sumofsquares"] = fitter.sqerror
        fit_curve.params["comment"] = fitter.commentstring
        fit_curve.params["curve_type"] = 'fit_curve'
        fit_curve.params["fit_function"] = fitter.func
        fit_curve.params["name"] = 'fit_' + func
        
        return fitter, fit_curve
    
def convert_from_numpy(val):
    if isinstance(val, numpy.bool_):
        return bool(val)    
    if isinstance(val, numpy.int):
        return int(val)
    if isinstance(val, numpy.str_):
        return str(val)
    return val
def load(filename):
    """loads the curve at filename"""
    with pandas.get_store(filename, "r") as store:
            data = store["data"]
    kwds = dict()
    with h5py.File(filename) as the_file:
        try:
            meta = the_file["params"]
        except KeyError:
            pass
        else:
            for key, value in meta.iteritems():
                kwds[key] = convert_from_numpy(value.value)
    curve = Curve()
    curve.set_data(data)
    curve.set_params(**kwds)
    return curve