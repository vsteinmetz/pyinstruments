from curvefinder.models import Curve, Tag, Window, \
                             InstrumentLogicalName, \
                             ScopeCurve, NaCurve, SpecAnCurve
import h5py
from curve import Curve as PiCurve
from pandas import HDFStore
from datastore.settings import MEDIA_ROOT
from django.utils.timezone import now
from django.core.files.storage import default_storage
import os

FIELDS = ["acquisition_type", \
              
              "input_port", \
              "output_port", \
              "start_time", \
              "record_length", \
              "coupling", \
              "full_range", \
              "format", \
              "offset", \
              "sample_rate", \
              "input_freq_max", \
              "input_impedance", \
              "channel", \
              "trace", \
              "measurement", \
              "detector_type", \
              "channel"]

FOREIGNKEYFIELDS = {"instrument_logical_name" : InstrumentLogicalName, 
                    "parent" : Curve}

class TagNotFound(ValueError):
    pass

def get_by_tag(*args):
    """
    get_by_tag("tag1", "tag2" ...)
    returns a list of all curves with the specified tags
    """
    
    curves = None
    for name in args:
        tag = Tag.objects.get(name = name)
        if curves:
            curves = curves & set(tag.curve_set.all())
        else:
            curves = set(tag.curve_set.all())
    
    picurves = []
    kwds = dict()
    for curve in curves:
        for field in FIELDS:
            val = curve.__getattribute__(field)
            if val:
                kwds[field] = val
        picurve = PiCurve(None, meta = kwds)
        picurve.load_data(os.path.join(MEDIA_ROOT, curve.data_file.name))
        picurves.append(picurve)
        
    return picurves

def find_meta_in_h5(h5file, meta_data_name):
    try:
        meta = h5file["meta"]
    except KeyError:
        return
    try:
        md = meta[meta_data_name]
    except KeyError:
        return
    return md.value

def try_add(curve, h5file, meta_data_name):
    """
    if an element is found in h5file["meta"]["meta_data_name"], sets this 
    element for the database object curve 
    """
    
    val = find_meta_in_h5(h5file, meta_data_name)
    curve.__setattr__(meta_data_name, val)
    
   
def add_or_create(curve, fieldname, related_class, new_name):
        try:
            related_class.objects.get(name = new_name)
        except InstrumentType.DoesNotExist:
            related_class.create(name = new_name)
        curve.__setattr__(fieldname, \
                          related_class.objects.get(name = new_name))


def curve_db_from_curve(curve):
    """
    returns a CurveDB child using the meta data found in the curve
    """

    types = {"Curve": Curve, \
             "NaCurve": NaCurve, \
             "SpecAnCurve": SpecAnCurve, \
             "ScopeCurve": ScopeCurve}
    (log_name, new) = InstrumentLogicalName.objects.get_or_create( \
                    name=curve.meta.instrument_logical_name)
    if curve.meta.curve_type == "ScopeCurve":
        kwds = {"acquisition_type" : curve.meta.acquisition_type, \
         "averaging" : curve.meta.averaging, \
         "start_time" : curve.meta.start_time, \
         "record_length": curve.meta.record_length, \
         "coupling" : curve.meta.coupling, \
         "full_range" : curve.meta.full_range, \
         "offset" : curve.meta.offset, \
         "sample_rate": curve.meta.sample_rate, \
         "input_freq_max": curve.meta.input_freq_max, \
         "input_impedance": curve.meta.input_impedance, \
         "channel" : curve.meta.channel}
    if curve.meta.curve_type == "SpecAnCurve":
        kwds = {"bandwidth": curve.meta.bandwidth, \
              "averaging":curve.meta.averaging, \
              "center_freq":curve.meta.center_freq, \
              "start_freq":curve.meta.start_freq, \
              "stop_freq":curve.meta.stop_freq, \
              "span":curve.meta.span, \
              "trace":curve.meta.trace, \
              "detector_type":curve.meta.detector_type}
    if curve.meta.curve_type == "NaCurve":
        kwds = {"bandwidth": curve.meta.bandwidth, \
              "averaging":curve.meta.averaging, \
              "center_freq":curve.meta.center_freq, \
              "start_freq":curve.meta.start_freq, \
              "stop_freq":curve.meta.stop_freq, \
              "span":curve.meta.span, \
              "input_port":curve.meta.input_port, \
              "output_port":curve.meta.output_port, \
              "format":curve.meta.format, \
              "channel":curve.meta.channel, \
              "measurement":curve.meta.measurement}
    return types[curve.meta.curve_type](data = curve.data, \
                                        meta = curve.meta, \
                                        instrument_logical_name=log_name, \
                                        **kwds)
 

def save_h5(h5filename, comment = "", tags = []):
    """
    Saves the h5 file at address h5filename in the database system.
    
    Since comment and tags are editable values, they aren't stored in the
    hdf5 file itself.
    
    The following fields in 'meta' of the hdf file will be used to fill 
    the parameters of the database. 
              
              "instrument_type", --> adds an entry if needed 
              "instrument_logical_name",  --> adds an entry if needed 
              "acquisition_type", 
              "bandwidth", 
              "averaging", 
              "center_freq", 
              "start_freq", 
              "stop_freq", 
              "span", 
              "input_port", 
              "output_port", 
              "start_time", 
              "record_length", 
              "coupling", 
              "range", 
              "offset", 
              "input_freq_max", 
              "input_impedance", 
              "channel", 
              "trace", 
              "measurement"
    
    Finally, instrument_logical_name and 
    """
    
    h5file = h5py.File(h5filename)
    curve = Curve()
    curve.data_file = h5filename
    
    for field in FIELDS:
        try_add(curve, h5file, field)
    
    instrument_type = find_meta_in_h5(h5file, "instrument_type")
    instrument_logical_name = \
                    find_meta_in_h5(h5file, "instrument_logical_name")
                    
    if instrument_type:
        add_or_create(curve, "instrument_type", \
                      InstrumentType, instrument_type)
    if instrument_logical_name:
        add_or_create(curve, "instrument_logical_name", \
                      InstrumentLogicalName, instrument_logical_name)
    curve.save()