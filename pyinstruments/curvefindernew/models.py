import pyinstruments.datastore
from pyinstruments.datastore.settings import MEDIA_ROOT
from curve import Curve

from PyQt4 import QtCore, QtGui
from django.db import models
import os
from datetime import datetime
import json
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
        
        return CurveDB.objects.filter(Q(floatparam__name__name=parname)|Q(stringparam__name__name=parname), *args, **kwds)
        
    def filter_float_param(self, parname, **kwds):
        """
        If you are looking for only those curves that have a parameter Q>1e6
        filter_float_param('Q', value_gte=1e6)
        """
        new_kwds = dict()
        for key, val in kwds.iteritems():
            query = 'param__floatparam__float_' + key
            new_kwds[query] = val
        return CurveDB.objects.filter(param__name__name=parname, **new_kwds)

    def filter_string_param(self, parname, **kwds):
        new_kwds = dict()
        for key, val in kwds.iteritems():
            query = 'param__stringparam__string_' + key
            new_kwds[query] = val
        return CurveDB.objects.filter(param__name__name=parname, **new_kwds)

class WrongTypeError(ValueError):
    pass

def get_column(name, type_):
    """
    If the column doesn't exists, creates a new one.
    If it exists and has the required type, returns the existing one
    otherwise throws a WrongTypeError.
    """
    col, new = ParamColumn.objects.get_or_create(name=name)
    if new:
        col.type = type_
        col.save()
    else:
        if col.type!=type_:
            raise WrongTypeError("column " + name + " allready exists and has the wong type " + type_)
    return col

class CurveDB(models.Model, Curve):
    """
    The base object containing the path to the curves, with all the meta 
    data associated.
    """
    
    objects = CurveManager()
       
    def __unicode__(self):
        return self.params["name"]

    tags_relation = models.ManyToManyField(Tag)
    tags_flatten = models.TextField(blank = True, null = True)
    #read only
    data_file = models.FileField(upload_to = '%Y/%m/%d')
    # parent curve e.g., for fit curve...
    parent = models.ForeignKey("self", \
                               related_name = 'childs', \
                               blank = True, \
                               null = True)
    
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
        subclasses = Param.__subclasses__()
        dic_param = dict()
        for cls in subclasses:
            name = cls.__name__.lower()
            param_set = self.__getattribute__(name + '_set')
            params = param_set.all()
            for par in params:
                dic_param[par.name_txt] = par.value
        self.set_params(**dic_param)
        return dic_param

    @property
    def params(self):
        if self._params is not None:
            return self._params
        else:
            self.load_params()
            return self._params
    
    def save_string_param(self, col, val):
        try:
            column = get_column(col, 'string')
        except WrongTypeError:
            column = get_column(col, 'text')
            param, new = TextParam.objects.get_or_create(col=column, curve=self, defaults={'value':val})
        param, new = StringParam.objects.get_or_create(col=column, curve=self, defaults={'value':val})
    
    def _save_generic_param(self, col, val, cls):
        column = get_column(col, cls.type)
        param, new = cls.objects.get_or_create(col=column, curve=self, defaults={'value':val})
        
    def save_num_param(self, col, val):
        self._save_generic_param(col, val, FloatParam)
        
    def save_date_param(self, col, val):
        self._save_generic_param(col, val, DateParam)
    
    def save_bool_param(self, col, val):
        self._save_generic_param(col, val, BooleanParam)        
        
    def save_params(self):
        for par, val in self.params.iteritems():
            if isinstance(val, basestring):
                self.save_string_param(par, val)
                continue
            if isinstance(val, bool):
                self.save_bool_param(par, val)
                continue
            if isinstance(val, (int, float, long)):
                self.save_num_param(par, val)
                continue
            if isinstance(val, datetime):
                self.save_date_param(par, val)
                continue
            raise ValueError('could not find the type of parameter ' + val)
    
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
    
    def set_default_params(self):
        """
        Set all required parameters that have a default to that value
        """
        
        columns = ParamColumn.objects.all()
        for col in columns:
            if col.required:
                if not col.name in self.params:
                    self.params[col.name] = col.default
        
    
    def save(self):
        """
        Saves the curve in the database. If the curve is data_read_only 
        The actual datafile will be saved only on the first call of save().
        """
        
        self.set_default_params()
        try:
            date = self.params["date"]
        except KeyError:
            date = datetime.now()
            self.params["date"] = date
        if not self.data_file:
            self.data_file = os.path.join( \
                    date.strftime('%Y/%m/%d'), \
                    self.params["name"] + '.h5')
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
    
class ParamColumn(models.Model):
    """
    Parameters can be easily looked up by name...
    """
    
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    type = models.CharField(max_length=255)
    required = models.BooleanField(default=False)
    default_json = models.CharField(max_length=1064)
    
    @property
    def default(self):
        if self.type == "date":
            return datetime.now()
        return json.loads(self.default_json)
    
    def __unicode__(self):
        return self.name
    
    
class Param(models.Model):
    """
    A parameter references a ParamColumn and a CurveDB
    """
    
    col = models.ForeignKey(ParamColumn)
    read_only = models.BooleanField(default=False)
    
    @property
    def name_txt(self):
        return self.col.name
    
    @name_txt.setter
    def name_txt(self, name):
        (pname, new) = ParamColumn.objects.get_or_create(name=name)
        self.name = pname
        return name
    
    @property
    def val(self):
        par_child = self.__getattribute__(self.type + 'param')
        return self.par_child.value
    
    @val.setter
    def val(self, value):
        if self.read_only:
            raise ValueError("parameter " + self.name_txt + "is read-only")
        par_child = self.__getattribute__(self.type + 'param')
        par_child.value = value
        return value
    
    def __unicode__(self):
        return self.col.name
    
class StringParam(Param):
    type = 'string'
    def __init__(self, *args, **kwds):
        super(StringParam, self).__init__(*args, **kwds)
    curve = models.ForeignKey(CurveDB)
    value = models.CharField(max_length = 255)
    
class FloatParam(Param):
    type = 'float'
    def __init__(self, *args, **kwds):
        super(FloatParam, self).__init__(*args, **kwds)
        
    curve = models.ForeignKey(CurveDB)
    value = models.FloatField()

class BooleanParam(Param):
    type = 'boolean'
    def __init__(self, *args, **kwds):
        super(BooleanParam, self).__init__(*args, **kwds)
        
    curve = models.ForeignKey(CurveDB)
    value = models.BooleanField()

class TextParam(Param):
    type = 'text'
    def __init__(self, *args, **kwds):
        super(TextParam, self).__init__(*args, **kwds)
        
        
    curve = models.ForeignKey(CurveDB)        
    value = models.TextField(blank = True)

class DateParam(Param):
    type = 'date'
    def __init__(self, *args, **kwds):
        super(DateParam, self).__init__(*args, **kwds)
        
    curve = models.ForeignKey(CurveDB)
    value = models.DateTimeField()

class ModelMonitor(QtCore.QObject):
    tag_added = QtCore.pyqtSignal()
    tag_deletted = QtCore.pyqtSignal()
model_monitor = ModelMonitor()