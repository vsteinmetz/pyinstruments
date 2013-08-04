from django.db import models
from django.core.urlresolvers import reverse
from model_utils import ChoiceEnum
import datastore
from curve import Curve
from datastore.settings import MEDIA_ROOT
from datetime import datetime
from django.core.files.storage import default_storage

import os
import pandas

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


class CurveDB(models.Model, Curve):
    """
    The base object containing the path to the curves, with all the meta 
    data associated.
    """   
    
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
    
    # parent curve e.g., for fit curve...
    parent = models.ForeignKey("self", \
                               related_name = 'childs', \
                               blank = True, \
                               null = True)
        
    #read only
    data_file = models.FileField(upload_to = '%Y/%m/%d')
    date_created = models.DateTimeField(auto_now_add=True, db_index = True)
    instrument_logical_name = models.ForeignKey(InstrumentLogicalName, \
                                                default = 1)
    #flags
    user_has_read = models.BooleanField(default = False, db_index=True)
    
    curve_types = ChoiceEnum('Curve', 'ScopeCurve', 'NaCurve', 'SpecAnCurve')
    data_read_only = models.BooleanField(default = True)
    curve_type  = models.IntegerField(max_length = 30, \
                                   choices = tuple(curve_types), \
                                   default = curve_types.Curve)
    
    def get_full_filename(self):
        return os.path.join(datastore.settings.MEDIA_ROOT, \
                                 self.data_file.name)
            
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
            super(CurveDB, self).save_in_file(self.get_full_filename())
        super(CurveDB, self).save()
            
            
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
  
class NaCurve(FrequencyCurve):
    """
    Model for traces acquired by a network analyzer
    """
    
    def __init__(self, *args, **kwds):
        super(NaCurve, self).__init__(*args, **kwds)
        curve_type = super(NaCurve, self).curve_types.NaCurve
        
    input_port = models.FloatField(blank = True)
    output_port = models.FloatField(blank = True)
    formats = ChoiceEnum("Real", \
                        "Polar", \
                        "LinMag", \
                        "GroupDelay", \
                        "Imag", \
                        "PPhase", \
                        "Smith", \
                        "UPhase", \
                        "SLinear", \
                        "SLogarithmic",\
                        "Complex")
    
    format = models.IntegerField(choices = formats, blank = True)
    
    averaging = models.IntegerField(blank = True)
    channel = models.CharField(max_length = 255, \
                                        null = True, \
                                        blank = True)
    measurement = models.CharField(max_length = 255, \
                                        null = True, \
                                        blank = True)
    
class SpecAnCurve(FrequencyCurve):
    """
    Model for traces acquired by a spectrum analyzer
    """
    
    def __init__(self, *args, **kwds):
        super(SpecAnCurve, self).__init__(*args, **kwds)
        curve_type = super(SpecAnCurve, self).curve_types.SpecAnCurve
        
    detector_types = ChoiceEnum("Sample", \
                                "Off", \
                                "Neg", \
                                "Average", \
                                "Pos", \
                                "Qpe", \
                                "Rav", \
                                "AverageAgain", \
                                "Norm", \
                                "Eav")
    
    averaging = models.IntegerField()
    detector_type = models.IntegerField(choices = detector_types, \
                                        blank = True)
    
    trace = models.CharField(max_length = 255, \
                                        null = True, \
                                        blank = True)
    
class ScopeCurve(CurveDB):
    """
    Model for traces acquired by an oscilloscope
    """
    
    def __init__(self, *args, **kwds):
        super(ScopeCurve, self).__init__(*args, **kwds)
        curve_type = super(ScopeCurve, self).curve_types.ScopeCurve
        
    acquisition_types = ChoiceEnum("normal", \
                                   "peakDetect", \
                                   "hiRes", \
                                   "enveloppe", \
                                   "average")
    
    averaging = models.IntegerField(blank = True)
    acquisition_type = models.IntegerField(choices = \
                                           acquisition_types, \
                                            blank = True)
    
    start_time = models.FloatField(blank = True)
    record_length  = models.IntegerField(blank = True)
    couplings = ChoiceEnum("AC", \
                           "DC", \
                           "GND")
    
    coupling = models.IntegerField(choices = couplings, blank = True)
    
    sample_rate = models.FloatField(blank = True)
    full_range = models.FloatField(blank = True)
    offset = models.FloatField(blank = True)
    input_freq_max = models.FloatField(blank = True)
    input_impedance = models.FloatField(blank = True)
    channel = models.CharField(max_length = 255, 
                                        blank = True)
    

    def get_absolute_url(self):
        return reverse('curves_detail', args=[self.id])
