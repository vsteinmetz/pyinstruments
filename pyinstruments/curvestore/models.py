import pyinstruments.datastore
from pyinstruments.datastore.settings import MEDIA_ROOT
from curve import Curve
from curve import load as load_curve

from PyQt4 import QtCore, QtGui
from django.db import models
import os
from datetime import datetime
import json
from django.core.files.storage import default_storage
from django.template.defaultfilters import slugify
import numpy
from django.core.exceptions import ObjectDoesNotExist


def top_level_tags():
    tag_names = set()
    ch = Tag.objects.all()
    for tag in ch:
        tag_names = tag_names.union([tag.name.split('/')[0]])
    tags = []
    for tag_name in tag_names:
        tag, created = Tag.objects.get_or_create(name=tag_name)
        tags.append(tag)
    return tags

class Tag(models.Model):
    """
    each curve can contain a list of tags. Tags could be hierarchical by 
    using something like: wafer1/sample1/structure2
    """
    
    name = models.CharField(max_length=200)

    @property
    def shortname(self):
        return self.name.split('/')[-1]
        
    def set_shortname(self, val):
        childs = self.childs()
        path = self.name.split('/')[:-1]
        if path:
            self.name = '/'.join(path) + '/' + val
        else:
            self.name = val
        self.save()
        for child in childs:
            child.move(self.name)
    
    def add_child(self, name):
        child, create = Tag.objects.get_or_create(name=self.name + '/' + name)
      
    def remove(self):
        """
        removes tag and all childs
        """  
        childs = self.childs()
        self.delete()
        for child in childs:
            child.remove()
    
    def move(self, new_parent):
        childs = self.childs()
        if new_parent=="":
            self.name = self.shortname
        else:
            self.name = new_parent + '/' + self.shortname
        self.save()
        for child in childs:
            child.move(self.name)
    
    def childs(self):
        childs_start = self.name + '/'
        len_strip = len(childs_start)
        ch = Tag.objects.filter(name__startswith=childs_start)
        child_str = set()
        for t in ch:
            stripped = t.name[len_strip:]
            child = stripped.split('/')[0]
            child_str = child_str.union([child])
        tags = []
        for child in child_str:
            fullchildname = self.name + '/' + child
            tag, created = Tag.objects.get_or_create(name=fullchildname)
            tags.append(tag)
        return tags
        
    def __unicode__(self):
        return self.name


            
##http://zmsmith.com/2010/04/using-custom-django-querysets/
class MyQuerySet(models.query.QuerySet):
    def filter_param(self, parname, **kwds):
        """
        If you are looking for only those curves that have a parameter Q:
        filter_param('Q')
        for Q values larger than 1e6 only:  filter_param('Q', value__gte=1e6)
        """
        
        column = ParamColumn.objects.get(name=parname)
        related_name = column.type + 'param'
        
        new_kwds = dict()
        new_kwds[related_name + '__col__name'] = parname
        for key, val in kwds.iteritems():
            new_kwds[related_name + '__' + key] = val
        return self.filter(**new_kwds)

    def filter_tag(self, tagname):
        """
        Return only those curve that have the tag tagname
        """
        #return self.filter_param('tags_flatten', value__contains=";"+tagname+";")
        return self.filter(tags_relation__name=tagname)

class CurveManager(models.Manager):
    """
    Custom manager to make easy researchs by tag
    """
    
    def get_query_set(self):
        return MyQuerySet(self.model)
    #def __getattr__(self, name):
    #    return getattr(self.get_query_set(), name)
    def filter_param(self, parname, **kwds):
        return self.get_query_set().filter_param(parname, **kwds)
    filter_param.__doc__ = MyQuerySet.filter_param.__doc__
    
    def filter_tag(self, tagname):
        return self.get_query_set().filter_tag(tagname)
    filter_tag.__doc__ = MyQuerySet.filter_tag.__doc__

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
            raise WrongTypeError("column " + name + " allready exists and has the wong type " + col.type + " not " + type_)
    return col


def default(obj):
    """Default JSON serializer."""
    import calendar, datetime

    if isinstance(obj, datetime.datetime):
        return obj.strftime("%y/%m/%d/%H/%M/%S/%f")

def date_to_date(dic):
    if 'date' in dic:
        dic['date'] = datetime.strptime(dic['date'], "%y/%m/%d/%H/%M/%S/%f")
    return dic
 
class CurveDB(models.Model, Curve):
    """
    The base object containing the path to the curves, with all the meta 
    data associated.
    """
    
    objects = CurveManager()
       
    def __unicode__(self):
        return self.name

    tags_relation = models.ManyToManyField(Tag)
    _name = models.CharField(max_length=255, default='some_curve')
    params_json = models.TextField(default="{}")
    #read only
    data_file = models.FileField(upload_to = '%Y/%m/%d')
    # parent curve e.g., for fit curve...
    parent = models.ForeignKey("self",
                               related_name = 'childs',
                               blank = True,
                               null = True)
    has_childs = models.BooleanField(default=False)
    saved_in_db = models.BooleanField(default=False)
    #for problems with django-evolution use:
    _date = models.DateTimeField(default=datetime.fromtimestamp(0))
    #date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        get_latest_by = "_date"
    
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
        dic_param = json.loads(self.params_json, object_hook=date_to_date)
        dic_param['tags_flatten'] = self.do_flatten_tags()
        self.set_params(**dic_param)
        self.set_default_params()
        return dic_param

    @property
    def params(self):
        if self._params is not None:
            return self._params
        else:
            self.load_params()
            return self._params
    
    def save_char_param(self, col, val):
        try:
            column = get_column(col, 'char')
        except WrongTypeError:
            self._save_generic_param(col, val, TextParam)            
        else:
            self._save_generic_param(col, val, CharParam)
                
    def _save_generic_param(self, col, val, cls):
        column = get_column(col, cls.type)
        param, new = cls.objects.get_or_create(col=column, curve=self, defaults={'value':val})
        if not new:
            if not column.read_only:
                param.value = val
                param.save()
            else:
                if param.value!=val:
                    print "Modified value of read_only parameter " + column.name + " was not saved!"
        
    def save_num_param(self, col, val):
        if numpy.isnan(val):
            val=1e100
        self._save_generic_param(col, val, FloatParam)
            
    def save_date_param(self, col, val):
        self._save_generic_param(col, val, DateParam)
    
    def save_bool_param(self, col, val):
        self._save_generic_param(col, val, BooleanParam)        
    
    @property
    def name(self):
        return self._name
    
    @name.setter
    def name(self, val):
        self._name = val
        self.params['name'] = val
        return val
    
    @property
    def date(self):
        return self._date
    
    @date.setter
    def date(self, val):
        self._date = val
        self.params['date'] = val
        return val
    
    def do_flatten_tags(self):
        return ';' + \
            ';'.join(self.tags) + \
            ';'
    
    def save_params(self):
        self._name = self.params["name"]
        self._date = self.params["date"]
        if not self.pk:
            models.Model.save(self)
        self.params["id"] = self.pk
        
        self.params["tags_flatten"] = self.do_flatten_tags()
        
        
        if self.parent is not None:
            self.params["parent_id"] = self.parent.pk
        elif not "parent_id" in self.params:
            self.params["parent_id"] = 0
        
        for par, val in self.params.iteritems():
            if isinstance(val, basestring):
                self.save_char_param(par, val)
                continue
            if isinstance(val, (bool, numpy.bool_)):
                self.save_bool_param(par, val)
                continue
            if isinstance(val, (numpy.integer, numpy.float)):
                val = float(val)
            if isinstance(val, (int, float, long)):
                self.save_num_param(par, val)
                continue
            if isinstance(val, datetime):
                self.save_date_param(par, val)
                continue
            raise ValueError('could not find the type of parameter ' + str(val))
        
        self.params_json = json.dumps(self.params, default=default)
        #models.Model.save(self)

    def get_full_filename(self):
        return os.path.join(MEDIA_ROOT, \
                                 self.data_file.name)
 
    def save_tags(self):
        for tag_txt in self.tags:
            (tag, new) = Tag.objects.get_or_create(name=tag_txt)
            if new:
                model_monitor.tag_added.emit()
            self.tags_relation.add(tag)

    
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
        if not self.data_file:
            self.data_file = os.path.join( \
                    self.params["date"].strftime('%Y/%m/%d'), \
                    slugify(self.name) + '.h5')
            full_path = self.get_full_filename()
            dirname = os.path.dirname(full_path)
            if not os.path.exists(dirname):
                os.makedirs(dirname) 
            full_path = default_storage.get_available_name(full_path)
            self.data_file = os.path.relpath(full_path, MEDIA_ROOT)
        
        #models.Model.save(self) #this way, the id is correct
        self.save_params() #this saves the curve with the correct id
        if not self.params["data_read_only"]:
            Curve.save(self, self.get_full_filename())
        else:
            if not os.path.exists(self.get_full_filename()):
                Curve.save(self, self.get_full_filename())
        self.save_tags()
        
        #if self.saved_in_db==False:
        #    self.saved_in_db=True
        #    models.Model.save(self)
        models.Model.save(self)
     
     
    def delete(self):
        try:
            os.remove(self.get_full_filename())
        except WindowsError:
            print 'no file found at ' + self.get_full_filename()
        super(CurveDB, self).delete()
        subclasses = Param.__subclasses__()
        dic_param = dict()
        for cls in subclasses:
            name = cls.__name__.lower()
            param_set = self.__getattribute__(name)
            params = param_set.all()
            for par in params:
                par.delete()
        
    def add_child(self, curve):
        curve.parent = self
        self.has_childs = True        
        self.save()
        curve.save()
        model_monitor.child_added.emit(self.id)

    def fit(self, func, autoguessfunction='', autosave=False, maxiter = 10, verbosemode = False,\
                    manualguess_params = {},fixed_params = {},graphicalfit=False):
        fitter, fit_curve = super(CurveDB, self).fit(
                        func,
                        autoguessfunction=autoguessfunction, 
                        maxiter=maxiter, 
                        verbosemode=verbosemode,
                        manualguess_params=manualguess_params,
                        fixed_params=fixed_params, 
                        graphicalfit=graphicalfit)
        
        fit_curve_db = curve_db_from_curve(fit_curve)
        fit_curve_db.name +='_of_' + str(self.id)
        fit_curve_db.params['window']=self.params["window"]
        if autosave:
            if "manualfit_concluded" in fit_curve_db.params:
                 if fit_curve_db.params["manualfit_concluded"]: 
                     self.add_child(fit_curve_db)
            else:
                self.add_child(fit_curve_db)
                
        model_monitor.fit_done.emit()
        return fit_curve_db
        
    
class ParamColumn(models.Model):
    """
    Parameters can be easily looked up by name...
    """
    
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    type = models.CharField(max_length=255)
    required = models.BooleanField(default=False)
    default_json = models.CharField(max_length=1064)
    read_only = models.BooleanField(default=False)
    
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
    class Meta:
        abstract = True
    
    col = models.ForeignKey(ParamColumn)
    
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
        if self.col.read_only:
            raise ValueError("parameter " + self.name_txt + "is read-only")
        par_child = self.__getattribute__(self.type + 'param')
        par_child.value = value
        return value
    
    def __unicode__(self):
        return self.col.name
    
class CharParam(Param):
    type = 'char'
    def __init__(self, *args, **kwds):
        super(CharParam, self).__init__(*args, **kwds)
    curve = models.ForeignKey(CurveDB, related_name='charparam')
    value = models.CharField(max_length = 255)
    
class FloatParam(Param):
    type = 'float'
    def __init__(self, *args, **kwds):
        super(FloatParam, self).__init__(*args, **kwds)
        
    curve = models.ForeignKey(CurveDB, related_name='floatparam')
    value = models.FloatField()

class BooleanParam(Param):
    type = 'boolean'
    def __init__(self, *args, **kwds):
        super(BooleanParam, self).__init__(*args, **kwds)
        
    curve = models.ForeignKey(CurveDB, related_name='booleanparam')
    value = models.BooleanField()

class TextParam(Param):
    type = 'text'
    def __init__(self, *args, **kwds):
        super(TextParam, self).__init__(*args, **kwds)

    curve = models.ForeignKey(CurveDB, related_name='textparam')        
    value = models.TextField(blank = True)

class DateParam(Param):
    type = 'date'
    def __init__(self, *args, **kwds):
        super(DateParam, self).__init__(*args, **kwds)
        
    curve = models.ForeignKey(CurveDB, related_name='dateparam')
    value = models.DateTimeField()

def curve_db_from_curve(curve):
    curve_db = CurveDB()
    curve_db.set_params(**curve.params)
    curve_db.set_data(curve.data)
    if 'name' in curve.params:
        curve_db.name = curve.params['name']
    if 'date' in curve.params:
        d = curve.params['date']
        if isinstance(d, basestring):
            curve_db.params["date"] = datetime.strptime(d, "%y/%m/%d/%H/%M/%S/%f")
        curve_db.date = curve_db.params['date']
    else:
        curve_db.date = datetime.now()
    if 'tags_flatten' in curve.params:
        curve_db.tags = curve.params['tags_flatten'].rstrip(";").split(";")[1:]
    return curve_db

class IdError(ValueError):
    pass
def curve_db_from_file(filename,inplace=False,overwrite=None):
    """overwrite = None: raise Exception if id conflict
       overvrite = True: overwrite id if conflict
       overvrite = False: use new id"""
    curve = load_curve(filename, with_data=not inplace)
    curve_db = CurveDB()
    if inplace:
        curve_db.data_file = os.path.relpath(filename, MEDIA_ROOT)
    id = int(curve.params['id'])
    try:
        old_one = CurveDB.objects.get(id=id)
    except ObjectDoesNotExist:
        curve_db.id = id
    else:
        if overwrite is None:
            raise IdError("Id " + str(id) + " already exists (attributed to " + old_one.params["name"] + ")! Don't know what to do with new curve \"" + curve.params["name"] + "\"")
        elif overwrite:
            old_one.delete()
            curve_db.id = id
            
    curve_db.set_params(**curve.params)
    curve_db.set_data(curve.data)
    if 'name' in curve.params:
        curve_db.name = curve.params['name']
    if 'date' in curve.params:
        d = curve.params['date']
        if isinstance(d, basestring):
            curve_db.params["date"] = datetime.strptime(d, "%y/%m/%d/%H/%M/%S/%f")
        curve_db.date = curve_db.params['date']
    else:
        curve_db.date = datetime.now()
    if 'tags_flatten' in curve.params:
        curve_db.tags = curve.params['tags_flatten'].rstrip(";").split(";")[1:]
    return curve_db

class ModelMonitor(QtCore.QObject):
    tag_added = QtCore.pyqtSignal()
    tag_deletted = QtCore.pyqtSignal()
    fit_done = QtCore.pyqtSignal()
    child_added = QtCore.pyqtSignal(int)
model_monitor = ModelMonitor()