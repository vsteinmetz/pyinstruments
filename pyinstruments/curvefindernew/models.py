import pyinstruments.datastore
from pyinstruments.datastore.settings import MEDIA_ROOT
from curve import Curve

from PyQt4 import QtCore, QtGui
from django.db import models
import os
from datetime import datetime
from django.core.files.storage import default_storage

class CurveType(models.Model):
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
            question = question & models.Q(tags_flatten__contains=\
                         ';' + str(Tag.objects.get(name=tag).pk) + ';')
        return super(CurveManager, self).filter(question)
        
    def filter_param(self, parname, *args, **kwds):
        """
        If you are looking for only those curves that have a parameter Q:
        filter_param('Q')
        """
        return CurveDB.objects.filter(param___name__name=parname, *args, **kwds)
        
    def filter_float_param(self, parname, **kwds):
        """
        If you are looking for only those curves that have a parameter Q>1e6
        filter_float_param('Q', value_gte=1e6)
        """
        new_kwds = dict()
        for key, val in kwds.iteritems():
            query = 'param__paramfloat__float_' + key
            new_kwds[query] = val
        return CurveDB.objects.filter(param___name__name=parname, **new_kwds)

class CurveDB(models.Model, Curve):
    """
    The base object containing the path to the curves, with all the meta 
    data associated.
    """
    
    objects = CurveManager()
       
    def __unicode__(self):
        return self.name

    name = models.CharField(max_length = 255, default="some_curve")
    comment = models.TextField(blank = True)
    tags_relation = models.ManyToManyField(Tag)
    tags_flatten = models.TextField(blank = True, null = True)
    _window = models.ForeignKey(Window, default = 1)
    #read only
    data_file = models.FileField(upload_to = '%Y/%m/%d')
    date_created = models.DateTimeField(auto_now_add=True, db_index = True)

    user_has_read = models.BooleanField(default = False, db_index=True)
    # parent curve e.g., for fit curve...
    parent = models.ForeignKey("self", \
                               related_name = 'childs', \
                               blank = True, \
                               null = True)
    data_read_only = models.BooleanField(default = True)
    curve_type  = models.ForeignKey(CurveType, default = 1)
    
    @property
    def window(self):
        return self._window.name
    
    @window.setter
    def window(self, name):
        (win, new) = Window.objects.get_or_create(name=name)
        self._window = win
        return name
    
    @property
    def tags(self):
        if not self._tags:
            if self.pk:
                self._tags = [tag.name for tag in self.tags_relation.all()]
            else:
                self._tags = []
        return self._tags
    
    @tags.setter
    def tags(self, val):
        self._tags = val
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


    def load_params(self):
        params = self.param_set.all()
        dic_param = dict()
        for par in params:
            dic_param[par.name] = par.value
        self.set_params(**dic_param)

    @property
    def params(self):
        if self._params is not None:
            return self._params
        else:
            self.load_params()
            return self._params
    
    def save_params(self):
        for par, val in self.params.iteritems():
            parname, new = ParamName.objects.get_or_create(name=par)
            if isinstance(val, basestring):
                param, new = ParamString.objects.get_or_create(_name=parname, curve=self, str_value=val)
            else:
                param, new = ParamFloat.objects.get_or_create(_name=parname, curve=self, float_value=val)
    
    def get_full_filename(self):
        return os.path.join(MEDIA_ROOT, \
                                 self.data_file.name)
 
    def save_tags(self):
        for tag_txt in self.tags:
            (tag, new) = Tag.objects.get_or_create(name=tag_txt)
            if new:
                model_monitor.tag_added.emit()
            self.tags_relation.add(tag)
        self.tags_flatten = ';' + \
                    ';'.join([str(tag.id) \
                                for tag in self.tags_relation.all()]) + \
                    ';'
    
    def save(self):
        """
        Saves the curve in the database. If the curve is data_read_only 
        The actual datafile will be saved only on the first call of save().
        """
        
        if not self.date_created:
            self.date_created = datetime.now()
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
        
        
        self.save_tags()

        super(CurveDB, self).save()
        self.save_params()
    
class ParamName(models.Model):
    """
    Parameters can be easily looked up by name...
    """
    
    name = models.CharField(max_length = 255)
    
    def __unicode__(self):
        return self.name
    
    
class Param(models.Model):
    """
    A parameter references a ParamName and a CurveDB
    """
    
    _name = models.ForeignKey(ParamName)
    curve = models.ForeignKey(CurveDB)
    read_only = models.BooleanField(default=False)
    type = models.CharField(max_length=255)
    
    @property
    def name(self):
        return self._name.name
    
    @name.setter
    def name(self, name):
        (pname, new) = ParamName.objects.get_or_create(name=name)
        self._name = pname
        return name
    
    @property
    def value(self):
        if self.type == "string":
            return self.paramstring.str_value
        if self.type == "float":
            return self.paramfloat.float_value
    
    def __unicode__(self):
        return self.name
    
class ParamString(Param):
    def __init__(self, *args, **kwds):
        super(ParamString, self).__init__(*args, **kwds)
        self.type = "string"
    
    str_value = models.CharField(max_length = 255)
    
class ParamFloat(Param):
    def __init__(self, *args, **kwds):
        super(ParamFloat, self).__init__(*args, **kwds)
        self.type = "float"
        
    float_value = models.FloatField()


class ModelMonitor(QtCore.QObject):
    tag_added = QtCore.pyqtSignal()
    tag_deletted = QtCore.pyqtSignal()
model_monitor = ModelMonitor()
    