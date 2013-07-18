from numpy import *
import pandas
import func
import numbers
from collections import OrderedDict
import numpy
#############################################################
## This module defines functions to do some elementary data treatment on DataFrames and Series, 
## The functions are added to DataFrame and Series
#############################################################
from my_data_structure import DataFrame,Series,monkey_add
from numpy import array



@monkey_add(pandas.DataFrame)
def fit_col(self,func,col = "data",**kwds):
    """applies Series.fit(func,**kwds) on self[col] and then appends a column to the dataset with the result"""
    res = self[col].fit(func,**kwds)
    if isinstance(func,basestring):
        newname = func
    else:
        newname =  func.__func__.__name__
    self["fit_" + newname] = res["fit_" + newname]
    setattr(self, newname + "_res",getattr(res, newname + "_res"))
    return self


@monkey_add(pandas.Series)
def fit(self,func,guess = None,Dfun=None, full_output=0, col_deriv=0, ftol=1.49012e-08, xtol=1.49012e-08, gtol=0.0, maxfev=0, epsfcn=0.0, factor=100, diag=None,**kwds):
    """optimizes func(self,par1,...parn) - self.values.
    func:
     - can also be a string, in this case, will look for an attribute self.func
    
    guess:
     - a dict containing guess arguments for the fit
     - If not provided, will look for a guess function named self.FUNCNAME_guess
     
     fixed parameters:
     - If extra kwds are given, they will be considered as fixed arguments for the fit
    
    returns:
     A dataframe containing
     - A column "data" with your data
     - A column "func_NAME_fit" containing the fitted curve
     - A property "custom.func_NAME_res" containing the best parameters.
    commonly used functions should be defined in ..func, with the naming convention func_lorentz, func_gauss ...
    """
    from scipy.optimize import leastsq
    if isinstance(func,basestring):
        func = getattr(self,func)
#    guess_given = True
    arguments = OrderedDict() ## should be orderedDict instead but I don t hav www connection to find the moduel now
    for k,v in zip(func.func_code.co_varnames[1:func.func_code.co_argcount],func.func_defaults):
        arguments[k] = v

    if guess == None:
#        guess_given = False
        try:
            guess_func = getattr(pandas.Series,func.__name__ + "_guess")
        except AttributeError:
            print "No guess provided, and no attribute func.guess either. Will use the defaults provided in the declaration"
            guess = dict()
        else:
            guess = guess_func(self)

    for k in kwds:
        guess.pop(k)
        arguments.pop(k)
       
    from functools import partial
    partial_func = partial(func,**kwds) ### the self gets absorbed in the partial
    
    remaining_keys = arguments.keys()
    
    if(len(kwds)>0):
        def new_func(args):
            keywords = dict(zip(remaining_keys,args))
            return array(partial_func(**keywords) - self.values, dtype = float)
    else:
        def new_func(args):
            return array(partial_func(*args) - self.values, dtype = float)
    arguments.update(guess)
            
    res = leastsq(new_func,list(arguments.values()),full_output=full_output, col_deriv=col_deriv, ftol=ftol, xtol=xtol, gtol=gtol, maxfev=maxfev, epsfcn=epsfcn, factor=factor, diag=diag)
   # print res

#    result = OrderedDict()
    keywords = dict(zip(remaining_keys,res[0]))
    keywords.update(kwds)
    newcolname = func.__func__.__name__ + "_fit"
    if self.name == None:
        name = "data"
    else:
        name = self.name
    df = pandas.DataFrame({name:self,newcolname:func(**keywords)})
    #setattr(df,func.__func__.__name__ + "_res",func.result_class(keywords,res))
    self.meta.set("fit")
    self.meta.fit.set(func.__func__.__name__)
    self.meta.fit[func.__func__.__name__] = func.result_class(keywords,res)
    return df




@monkey_add(pandas.Series)
def mean(self):
    #try:
    #    res = numpy.mean(self)
    #except ComplexWarning:
    #    res = pandas.Series.real.mean(self) + 1j*(pandas.Series.imag.mean(self))
    return numpy.mean(self.values)
    
@monkey_add(pandas.Series)
def re_im(self):
    return pandas.DataFrame({"re":real(self),"im":imag(self)}) 

@monkey_add (pandas.Series)
def update_custom(self,property,**kwds):
        self.custom.__getattribute__(property).update(kwds)

@monkey_add(pandas.Series)
def norm_corr(self,t2,mode = "valid"):
    """returns the normalized correlations between self and t2, for a series of delays
    if the 2 tables have same length and the mode is"valid", then only correlations at 0 time delay is calculated.
    see numpy.correlate for further help on the possible modes"""
    Y = correlate(array(self),array(t2),mode)/sum(abs(self)*abs(t2))
    X = self.index[:len(Y)]
    return  pandas.Series(Y,index = X)

@monkey_add(pandas.DataFrame)
def new_col_or_df(self,s):
    """if df is not empty, simply creates a new column with the serie as data, otherwise adds the column and uses its indexes"""
    if self.empty:
        df = pandas.DataFrame(s)
    else:
        df = self.join(s)
    return df

@monkey_add(pandas.Series)
def smart_corr(self,t2,frac = 0.99):
    """returns a pandas dataFrame containing several columns:
    - column "z1" is sel
    - column "z2" is t2
    ---> Indexes are the common times
    - column "norm_corr" are the normalized correlations between z1 and z2 obtained for negative times by sliding a fraction frac of dataset z1 along dataset z2
    and for positive times, by sliding a fraction frac of dataset z2 along dataset z1. Only 2*frac*len(t1 or t2) is hence generated.
    Unspecified behaviour if len(t1!=len(t2))   
    """
    Ypos = self.norm_corr(t2[:int(len(t2)*frac)])
    Ypos.index = array(Ypos.index) - Ypos.index[0]
    Yneg = t2.norm_corr(self[:int(len(self)*frac)]).conj()
    Yneg.index = Yneg.index[0]-array(Yneg.index)
    r = pandas.DataFrame({"z1":self,"z2":t2,"norm_corr":Ypos.add(Yneg,fill_value = 0)})
    r["norm_corr"][0]/=2
    r.custom = Custom()
    if hasattr(self,"custom"):
        r.custom.z1 = self.custom
    if hasattr(t2,"custom"):
        r.custom.z2 = t2.custom 
    return  r
