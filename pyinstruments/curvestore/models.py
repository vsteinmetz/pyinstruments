import pyinstruments.datastore
from pyinstruments.datastore.settings import MEDIA_ROOT
from curve import Curve
from curve import load as load_curve

import copy
from django.db import transaction
from django.db.models import Q
from PyQt4 import QtCore, QtGui
from django.db import models
import os
from datetime import datetime
import json
from django.core.files.storage import default_storage
from django.template.defaultfilters import slugify
import numpy
from django.core.exceptions import ObjectDoesNotExist
import time
PROFILING = False
PROFILE_SAVE = False
TIC = 0

def profile(flag=PROFILING, text="", tic=None):
    if flag:
        if tic is not None:
            print text, time.time() - tic
        tic = time.time()
        return tic
    
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
            newname = '/'.join(path) + '/' + val
        else:
            newname = val
        try:
            Tag.objects.get(name=newname)
        except ObjectDoesNotExist:
            self.name = newname
            self.save()
            for child in childs:
                child.move(self.name)
        else:
            raise ValueError("A tag with name " + val + "already exists there")
    
    def add_child(self, name):
        return Tag.objects.get_or_create(name=self.name + '/' + name)
        
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
            new_name = self.shortname
        else:
            new_name = new_parent + '/' + self.shortname
        try:
            Tag.objects.get(name=new_name)
        except ObjectDoesNotExist:  
            pass
        else:
            raise ValueError("a tag with name " + new_name + " already exist")
        
        self.name = new_name
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
        q1 = Q(tags_relation__name__contains=tagname + "/") ##parent tag
        q2 = Q(tags_relation__name=tagname) ##tag itself
        return self.filter(q1|q2)

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
            if col.type not in ('char', 'text') and  type_ not in ('char', 'text'):
                raise WrongTypeError("column " + name + " already exists and has the wrong type " + col.type + " not " + type_)
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
        if self._tags==None:
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
        if PROFILING:
            print """
           
            """
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
            
        if PROFILING:
            import time
            tic = time.time()
        qs_float = self.floatparam.all().select_related('col')
        float_params   = dict([(v.name_txt, v) for v in qs_float])
        boolean_params = dict([(v.name_txt, v) for v in self.booleanparam.all().select_related('col')])
        char_params    = dict([(v.name_txt, v) for v in self.charparam.all().select_related('col')])
        text_params    = dict([(v.name_txt, v) for v in self.textparam.all().select_related('col')])
        date_params    = dict([(v.name_txt, v) for v in self.dateparam.all().select_related('col')])
        if PROFILING:
            print "time for queries: ", time.time() - tic 
        
        params = float_params
        params.update(boolean_params)
        params.update(char_params)
        params.update(text_params)
        params.update(date_params)
        
        to_add = dict()
        subclasses = Param.__subclasses__()
        #dic_param = dict()
        for cls in subclasses:
            to_add[cls.type] = []
        
        if PROFILING:
            tic = time.time()
            total = 0
            total_save = 0
            total_get_type = 0
            total_else = 0
        
        
        columns = None
        
        for par, val in self.params.iteritems():
            try:
                db_param = params.pop(par)
            except KeyError:
                if PROFILING:
                    tuc = time.time()
                cls = self.get_type(val)
                if PROFILING:
                    total_get_type+= time.time() - tuc
                if PROFILING:
                    toc = time.time()
                if not columns:
                    if PROFILING:
                        tac = time.time()
                    columns = dict([(o.name, o) for o in ParamColumn.objects.filter(name__in=self.params.keys())])
                    if PROFILING:
                        print "querying columns already in db: ", time.time() - tac
                try:
                    column = columns[par]#get_column(par, cls.type)
                except KeyError:
                    column = get_column(par, cls.type)
                if PROFILING:
                    total+=time.time() - toc
                if column.type=='text':
                    cls = TextParam
                if column.type=='char':
                    cls = CharParam

                to_add[column.type].append((column, self, val))
#                param, new = cls.objects.get_or_create(col=column,
#                                                       curve=self,
#                                                       defaults={'value':val})
            else:
                if PROFILING:
                    tyc = time.time()
                if db_param.value!=val:
                    if not db_param.col.read_only:
                        db_param.value = val
                        if PROFILING:
                            tec = time.time()
                        db_param.save()
                        if PROFILING:
                            total_save+= time.time()-tec
                    else:
                        print "Modified value of read_only parameter " + par + " was not saved!"
                if PROFILING:
                    total_else+= time.time() - tyc
        if PROFILING:
            print "total time get_type: ", total_get_type
            print "total time get_column: ", total
            print "total time else: ", total_else
            print "total time save: ", total_save
            print "lot of time here ?: ", time.time() - tic 

        if PROFILING:
            toc = time.time()
        for cls in subclasses:
            add_list = to_add[cls.type]
            cls.objects.bulk_create([cls(col=col, curve=curve, value=val) for (col, curve, val) in add_list])
 #           for (col, curve, val) in add_list:
 #               param, new = cls.objects.get_or_create(col=col,
 #                                                      curve=curve,
 #                                                      defaults={'value':val})     
        if PROFILING:
            print "total time for create parameters: ", time.time() - toc
        ## parameters left over in params should be deleted
        for val in params.values():
            val.delete()
        
        if PROFILING:
            tic = time.time()
        self.params_json = json.dumps(self.params, default=default)
        if PROFILING:
            print "total time for json: ", time.time() - tic
        
        #models.Model.save(self)
        
    def get_type(self, val):
        if isinstance(val, basestring):
            return CharParam
        if isinstance(val, (bool, numpy.bool_)):
            return BooleanParam
        if isinstance(val, (numpy.integer, numpy.float)):
            return FloatParam
        if isinstance(val, (int, float, long)):
            return FloatParam
        if isinstance(val, datetime):
            return DateParam
        raise ValueError('could not find the type of parameter ' + str(val))
        


    def get_full_filename(self):
        return os.path.join(MEDIA_ROOT, \
                                 self.data_file.name)
 
    def save_tags(self):
        tags = copy.deepcopy(self.tags)
        for tag in self.tags_relation.all():
            try:
                tags.remove(tag.name)
            except ValueError:
                self.tags_relation.remove(tag)
        # remaining tags have to be added
        for tag_name in tags:
            (tag, new) = Tag.objects.get_or_create(name=tag_name)
            if new:
                model_monitor.tag_added.emit()
            self.tags_relation.add(tag)
        """
        for tag_txt in self.tags:
            (tag, new) = Tag.objects.get_or_create(name=tag_txt)
            if new:
                model_monitor.tag_added.emit()
            self.tags_relation.add(tag)
        """
    
    def set_default_params(self):
        """
        Set all required parameters that have a default to that value
        """
        
        columns = ParamColumn.objects.all()
        for col in columns:
            if col.required:
                if not col.name in self.params:
                    self.params[col.name] = col.default        

    @transaction.commit_on_success
    def save(self):
        """
        Saves the curve in the database. If the curve is data_read_only 
        The actual datafile will be saved only on the first call of save().
        """
        tic = profile(PROFILE_SAVE, "start: ")
        
        self.set_default_params()
        tic = profile(PROFILE_SAVE, "set_defaults: ", tic)
        
        
        #models.Model.save(self) #this way, the id is correct
        
        tic = profile(PROFILE_SAVE, "other default assignements: ", tic)
        self.save_params() #this saves the curve with the correct id
        
        
        if not self.data_file:
            self.data_file = os.path.join( \
                    self.params["date"].strftime('%Y/%m/%d'), \
                    slugify(str(self.id) +"_"+ self.name) + '.h5')
            full_path = self.get_full_filename()
            dirname = os.path.dirname(full_path)
            
            tic = profile(PROFILE_SAVE, "format dirname: ", tic)
            
            if not os.path.exists(dirname):
                os.makedirs(dirname) 
            tic = profile(PROFILE_SAVE, "create dir: ", tic)
            full_path = default_storage.get_available_name(full_path)
            tic = profile(PROFILE_SAVE, "get_available_name: ", tic)
            self.data_file = os.path.relpath(full_path, MEDIA_ROOT)
            tic = profile(PROFILE_SAVE, "set datafile: ", tic)
        
        
        
        tic = profile(PROFILE_SAVE, "save_params: ", tic)
        if not self.params["data_read_only"]:
            Curve.save(self, self.get_full_filename())
            tic = profile(PROFILE_SAVE, "Curve.save(): ", tic)
        else:
            if not os.path.exists(self.get_full_filename()):
                Curve.save(self, self.get_full_filename())
                tic = profile(PROFILE_SAVE, "Curve.save(): ", tic)
        self.save_tags()
        tic = profile(PROFILE_SAVE, "save tags ", tic)
        #if self.saved_in_db==False:
        #    self.saved_in_db=True
        #    models.Model.save(self)
        models.Model.save(self)
        tic = profile(PROFILE_SAVE, "Model.save(): ", tic)
    @transaction.commit_on_success
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
            params.delete()
        
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
    value = models.CharField(max_length=255)
    
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
    """overwrite=None: raise Exception if id conflict
       overwrite=True: overwrite id if conflict
       overwrite=False: use new id"""
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

def clear_unused_columns():
    print "clearing unused columns"
    for col in ParamColumn.objects.all():
        if col.__getattribute__(col.type + "param_set").count()==0:
            print "clearing column: " + col.name
            col.delete()

clear_unused_columns() #at each startup            
        
class ModelMonitor(QtCore.QObject):
    tag_added = QtCore.pyqtSignal()
    tag_deletted = QtCore.pyqtSignal()
    fit_done = QtCore.pyqtSignal()
    child_added = QtCore.pyqtSignal(int)
model_monitor = ModelMonitor()