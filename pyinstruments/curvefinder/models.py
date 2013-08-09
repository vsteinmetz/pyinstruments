from pyinstruments.utils.curve import Curve
import pyinstruments.datastore
from pyinstruments.pyhardware import choices
from pyinstruments.datastore.settings import MEDIA_ROOT

from django.db import models
from django.core.urlresolvers import reverse
from model_utils import Choices
from datetime import datetime
from django.core.files.storage import default_storage
import os
import pandas
from numpy import array, sin
from collections import OrderedDict
import json


class InstrumentLogicalName(models.Model):
    """
    The name of the instrument that recorded the curve on the initial 
    machine
    """
    name = models.CharField(max_length=200)
    
    def __unicode__(self):
        return self.name
 
class Tag(models.Model):
    """
    each curve can contain a list of tags. Tags could be hierarchical by 
    using something like: wafer1/sample1/structure2
    """
    
    name = models.CharField(max_length=200)
   
    def __unicode__(self):
        return self.name
    
class Window(models.Model):
    """
    The window where to plot the curve by default.
    """   
    
    name = models.CharField(max_length=200)
    
    def __unicode__(self):
        return self.name



class CurveManager(models.Manager):
    """
    Custom manager to make easy researchs by tag
    """
    
    def filter_tags_required(self, *args):
        """
        returns only the curves that contains all the required tags
        """
        
        question = models.Q()
        for tag in args:
            question = question & models.Q(tags_flatten__contains = \
                         ';' + str(Tag.objects.get(name = tag).pk) + ';')
        return super(CurveManager, self).filter(question)


class CurveDB(models.Model, Curve):
    """
    The base object containing the path to the curves, with all the meta 
    data associated.
    """   
    
    objects = CurveManager()
    
    def __init__(self, *args, **kwds):
        data = kwds.pop("data", None)
        meta = kwds.pop("meta", dict())
        models.Model.__init__(self, *args, **kwds)
        Curve.__init__(self, data=data, meta=meta)
        self.date_created = datetime.now()

    def __unicode__(self):
        return self.name

    name = models.CharField(max_length = 255, default="some_curve")
    comment = models.TextField(blank = True)
    tags = models.ManyToManyField(Tag, default = [1])
    window = models.ForeignKey(Window, default = 1)
    

        
    #read only
    data_file = models.FileField(upload_to = '%Y/%m/%d')
    date_created = models.DateTimeField(auto_now_add=True, db_index = True)
    instrument_logical_name = models.ForeignKey(InstrumentLogicalName, \
                                                default = 1)
    #flags
    tags_flatten = models.TextField(blank = True, null = True)
    user_has_read = models.BooleanField(default = False, db_index=True)
       
    # parent curve e.g., for fit curve...
    parent = models.ForeignKey("self", \
                               related_name = 'childs', \
                               blank = True, \
                               null = True)
    
    data_read_only = models.BooleanField(default = True)
    
    curve_types = Choices('Curve', 'ScopeCurve', 'NaCurve', 'SpecAnCurve')
    curve_type  = models.CharField(max_length = 100, \
                                   choices = tuple(curve_types), \
                                   default = curve_types.Curve)
    
    def get_full_filename(self):
        return os.path.join(pyinstruments.datastore.settings.MEDIA_ROOT, \
                                 self.data_file.name)
    
    
    def fit(self, func, guess = None, autosave = False):
        """
        Makes a fit of the curve and returns the child fit curve
        """
        
        import pandas
        data = pandas.Series(sin(array(self.data.index)), index = self.data.index)
        fit_curve = FitCurveDB(data=data, parent=self)
        fit_curve.fit_params = {'foo':4, 'bar':6}
        if autosave:
            fit_curve.save()
        return fit_curve
    
    def save(self):
        """
        Saves the curve in the database. If the curve is data_read_only 
        The actual datafile will be saved only on the first call of save().
        """
        
        if not self.data_file:
            self.data_file = os.path.join( \
                    self.date_created.strftime('%Y/%m/%d'), \
                    self.name + '.h5')
            full_path = self.get_full_filename()
            dirname = os.path.dirname(full_path)
            if not os.path.exists(dirname):
                os.makedirs(dirname) 
            full_path = default_storage.get_available_name(full_path)
            self.data_file = os.path.relpath(full_path, MEDIA_ROOT)
        if (self.pk is None) or (not self.data_read_only):
            Curve.save(self, self.get_full_filename())
        
        if self.pk == None:
            super(CurveDB, self).save()
                
        self.tags_flatten = ';' + \
                            ';'.join([str(tag.id) \
                                        for tag in self.tags.all()]) + \
                            ';'
        super(CurveDB, self).save()
    
           
    @property
    def tags_txt(self):
        return [tag.name for tag in self.tags.all()]
    
    @tags_txt.setter
    def tags_txt(self, val):
        for tag_txt in val:
            (tag, new) = Tag.objects.get_or_create(name = tag_txt)
            self.tags.add(tag)
        return val
    
    def delete(self):
        """deletes the entry in the database and the file"""
        
        try:
            os.remove(self.get_full_filename())
        except WindowsError:
            print 'no file found at ' + self.get_full_filename()
        super(CurveDB, self).delete()
    
    @property
    def window_txt(self):
        return self.window.name
    
    @window_txt.setter
    def window_txt(self, val):
        (win, new) = Window.objects.get_or_create(name = val)
        self.window = win
        return val
     
    @property
    def data(self):
        if self._data is not None:
            return self._data
        else:
            self.load_data(self.get_full_filename())
            return self._data

    @data.setter
    def data(self, table):
        if self.data_read_only:
            if self.pk is not None:
                raise ValueError(\
                    "Trying to modify the data in a read-only curve")
        self._data = table
    
    SUBCLASSES = \
        {curve_types.Curve:'curve', \
         curve_types.NaCurve:'frequencycurve', \
         curve_types.SpecAnCurve:'frequencycurve', \
         curve_types.ScopeCurve:'scopecurve'}
    
    def get_subclass(self):
        if self.curve_type == self.curve_types.Curve:
            return self 
        return self.__getattribute__(self.SUBCLASSES[self.curve_type])\
                                                            .get_subclass()

    def get_subclass_fields(self):
        return self.get_subclass().get_fields_as_text_ordered_dict()

    def get_fields_as_text_ordered_dict(self):
        return OrderedDict()



class FrequencyCurve(CurveDB):
    """
    Model for traces acquired by a Fourier-space measurement device 
    (i.e.: Network analyzer and Scope)
    """
    
    center_freq = models.FloatField(blank = True)
    start_freq = models.FloatField(blank = True)
    stop_freq = models.FloatField(blank = True)
    span = models.FloatField(blank = True)
    bandwidth = models.FloatField(blank = True)
    
    def get_fields_as_text_ordered_dict(self):
        dic = OrderedDict()
        dic["center_freq"] = str(self.center_freq)
        dic["start_freq"] = str(self.start_freq)
        dic["stop_freq"] = str(self.stop_freq)
        dic["span"] = str(self.span)
        dic["bandwidth"] = str(self.bandwidth)
        return dic
    
    
    SUBCLASSES = \
        {CurveDB.curve_types.NaCurve:'nacurve', \
         CurveDB.curve_types.SpecAnCurve:'specancurve'}
  
class NaCurve(FrequencyCurve):
    """
    Model for traces acquired by a network analyzer
    """
    
    def __init__(self, *args, **kwds):
        super(NaCurve, self).__init__(*args, **kwds)
        curve_type = super(NaCurve, self).curve_types.NaCurve
        
    input_port = models.FloatField(blank = True)
    output_port = models.FloatField(blank = True)
    formats = choices.na_formats
    
    format = models.CharField(max_length = 100, choices = formats, blank = True)
    
    averaging = models.IntegerField(blank = True)
    channel = models.CharField(max_length = 255, \
                                        null = True, \
                                        blank = True)
    measurement = models.CharField(max_length = 255, \
                                        null = True, \
                                        blank = True)
    
    def get_subclass(self):
        return self
    
    def get_fields_as_text_ordered_dict(self):
        dic = super(NaCurve, self).get_fields_as_text_ordered_dict()
        dic["input_port"] = str(self.input_port)
        dic["output_port"] = str(self.output_port)
        dic["format"] = str(self.formats._choice_dict[self.format])
        dic["averaging"] = str(self.averaging)
        dic["channel"] = str(self.channel)
        dic["measurement"] = str(self.measurement)
        return dic
        
class SpecAnCurve(FrequencyCurve):
    """
    Model for traces acquired by a spectrum analyzer
    """
    
    def __init__(self, *args, **kwds):
        super(SpecAnCurve, self).__init__(*args, **kwds)
        curve_type = super(SpecAnCurve, self).curve_types.SpecAnCurve
        
    detector_types = choices.spec_an_detector_types
    acquisition_types = choices.spec_an_acquisition_types
    
    averaging = models.IntegerField()
    detector_type = models.CharField(max_length = 100, choices = detector_types, \
                                        blank = True)
    acquisition_type = models.CharField(max_length = 100, choices = acquisition_types, \
                                        blank = True)
    
    trace = models.CharField(max_length = 255, \
                                        null = True, \
                                        blank = True)
    
    def get_fields_as_text_ordered_dict(self):
        dic = super(SpecAnCurve, self).get_fields_as_text_ordered_dict()
        dic["averaging"] = str(self.averaging)
        dic["detector_type"] = str(self.detector_types._choice_dict[self.detector_type])
        dic["trace"] = str(self.trace)
        return dic
    
    def get_subclass(self):
        return self
    
class ScopeCurve(CurveDB):
    """
    Model for traces acquired by an oscilloscope
    """
    
    def __init__(self, *args, **kwds):
        super(ScopeCurve, self).__init__(*args, **kwds)
        curve_type = super(ScopeCurve, self).curve_types.ScopeCurve
        
    acquisition_types = choices.scope_acquisition_types
    
    averaging = models.IntegerField(blank = True)
    acquisition_type = models.CharField(max_length = 100, choices = \
                                           acquisition_types, \
                                            blank = True)
    
    start_time = models.FloatField(blank = True)
    record_length  = models.IntegerField(blank = True)
    couplings = choices.scope_couplings
    
    coupling = models.CharField(max_length = 100, choices = couplings, blank = True)
    
    sample_rate = models.FloatField(blank = True)
    full_range = models.FloatField(blank = True)
    offset = models.FloatField(blank = True)
    input_freq_max = models.FloatField(blank = True)
    input_impedance = models.FloatField(blank = True)
    channel = models.CharField(max_length = 255, 
                                        blank = True)
    

    def get_absolute_url(self):
        return reverse('curves_detail', args=[self.id])

    def get_subclass(self):
        return self

    def get_fields_as_text_ordered_dict(self):
        dic = OrderedDict()
        dic["averaging"] = str(self.averaging)
        dic["acquisition_type"] = str(self.acquisition_types.\
                                      _choice_dict[self.acquisition_type])
        dic["start_time"] = str(self.start_time)
        dic["record_length"] = str(self.record_length)
        dic["coupling"] = str(self.couplings.\
                                      _choice_dict[self.coupling])
        dic["sample_rate"] = str(self.sample_rate)
        dic["full_range"] = str(self.full_range)
        dic["offset"] = str(self.offset)
        dic["input_freq_max"] = str(self.input_freq_max)
        dic["input_impedance"] = str(self.input_impedance)
        dic["channel"] = str(self.channel)
        return dic

def curve_db_from_curve(curve):
    """
    returns a CurveDB child using the meta data found in the curve
    """

    types = {"CurveDB": CurveDB, \
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
                                curve_type = curve.meta.curve_type, \
                                **kwds)


class FitCurveDB(CurveDB):
    fit_params_json = models.TextField()
    fit_function = models.CharField(max_length = 255)

    @property
    def fit_params(self):
        return json.loads(self.fit_params_json)
    
    @fit_params.setter
    def fit_params(self, params):
        self.fit_params_json = json.dumps(params, self.fit_params_json)
        return params