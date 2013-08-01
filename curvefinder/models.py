from django.db import models
from django.core.urlresolvers import reverse

class InstrumentType(models.Model):
    """
    Could be a Scope, Na, or SpecAn for instance...
    """
    name = models.CharField(max_length=200)
    
    def __unicode__(self):
        return self.name
    
class InstrumentLogicalName(models.Model):
    """
    The name of the instrument that recorded the curve on the initial machine
    """
    name = models.CharField(max_length=200)
    
    def __unicode__(self):
        return self.name
 
class Tag(models.Model):
    """
    each curve can contain a list of tags. Tags could be hierarchical by using
    wafer1/sample1/structure2
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
    The base object containing the path to the curves, with all the meta data
    associated.
    """   
    
    def __unicode__(self):
        return self.name

    name = models.CharField(max_length = 255, null = True, blank = True)

    #rewrittable metadata
    comment = models.TextField(blank = True)
    tags = models.ManyToManyField(Tag, default = [1])
    
    #plotting
    window = models.ForeignKey(Window, default = 1)
    user_has_read = models.BooleanField(default = False, db_index=True)
        
    data_file = models.FileField(upload_to = '%Y/%m/%d')
    date_created = models.DateTimeField(auto_now_add=True, db_index = True)

    
    
    
    #read only metadata
    acquisition_type = models.CharField(max_length = 255, \
                                        null = True, \
                                        blank = True)
    
    instrument_type = models.ForeignKey(InstrumentType, default = 1)
    instrument_logical_name = models.ForeignKey(InstrumentLogicalName, \
                                                default = 1)
    
    ### NA + SA
    bandwidth = models.FloatField(null = True, blank = True)
    averaging = models.IntegerField(null = True, blank = True)
    center_freq = models.FloatField(null = True, blank = True)
    start_freq = models.FloatField(null = True, blank = True)
    stop_freq = models.FloatField(null = True, blank = True)
    span = models.FloatField(null = True, blank = True)
    detector_type = models.IntegerField(null = True, blank = True)
    
    ### NA FIELDS
    input_port = models.FloatField(null = True, blank = True)
    output_port = models.FloatField(null = True, blank = True)
    format = models.CharField(max_length = 255, \
                                        null = True, \
                                        blank = True)
    
    ### SCOPE FIELDS
    start_time = models.FloatField(null = True, blank = True)
    record_length  = models.IntegerField(null = True, blank = True)
    coupling = models.CharField(max_length=2, choices = \
                                [("AC", "AC"), \
                                ("DC", "DC"), \
                                ("GD", "GND")], null = True, blank = True)
    sample_rate = models.FloatField(null = True, blank = True)
    range = models.FloatField(null = True, blank = True)
    offset = models.FloatField(null = True, blank = True)
    input_freq_max = models.FloatField(null = True, blank = True)
    input_impedance = models.FloatField(null = True, blank = True)
    
    ## IVI repeated capabilities stuff
    channel = models.CharField(max_length = 255, \
                                        null = True, \
                                        blank = True)
    trace = models.CharField(max_length = 255, \
                                        null = True, \
                                        blank = True)
    measurement = models.CharField(max_length = 255, \
                                        null = True, \
                                        blank = True)

    def get_absolute_url(self):
        return reverse('curves_detail', args=[self.id])
