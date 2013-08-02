from django.db import models
from django.core.urlresolvers import reverse
from model_utils import ChoiceEnum

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


class Curve(models.Model):
    """
    The base object containing the path to the curves, with all the meta 
    data associated.
    """   
    
    def __unicode__(self):
        return self.name

    name = models.CharField(max_length = 255)
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
    #flag
    user_has_read = models.BooleanField(default = False, db_index=True)
    
    curve_types = ChoiceEnum('Curve', 'ScopeCurve', 'NaCurve', 'SpecAnCurve')
    
    curve_type  = models.IntegerField(max_length = 30, \
                                   choices = tuple(curve_types))
    

class FrequencyCurve(Curve):
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
        super(FrequencyCurve, self).__init__(curve_type = \
                                             Curve.curve_types.NaCurve, \
                                             *args, **kwds)
        
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
        super(SpecAnCurve, self).__init__(curve_type = \
                                             Curve.curve_types.SpecAnCurve, \
                                             *args, **kwds)
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
    
    detector_type = models.IntegerField(choices = detector_types, \
                                        blank = True)
    
    trace = models.CharField(max_length = 255, \
                                        null = True, \
                                        blank = True)
    
class ScopeCurve(Curve):
    """
    Model for traces acquired by an oscilloscope
    """
    
    def __init__(self, *args, **kwds):
        super(ScopeCurve, self).__init__(curve_type = \
                                             Curve.curve_types.ScopeCurve, \
                                             *args, **kwds)
        
    acquisition_types = ChoiceEnum("averge", \
                         "normal", \
                         "hiRes", \
                         "peakDetect", \
                         "enveloppe")
    
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
