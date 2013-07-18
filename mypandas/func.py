from numpy import *
from pandas import Series,DataFrame
import functools
import my_data_structure


class default_result(my_data_structure.MetaData):
    """this is the default class object used to store fit results. The class is appended to Series.
    The instances of the class, containing particular fit results are appended to the series' metadata,
    with the name s.meta.fit"""
    def __init__(self,kwds,res):
        self.set("kwds")
        self.kwds.set(**kwds)
        self.set(flag = res[1])
        
class result_pdh(default_result):
    def linewidth(self,mod_freq):
        """returns the linewidth of the cavity given the modulation frequency of the pdh"""
        return self.kwds["width"]/self.kwds["mod"]*mod_freq


def add_to_series_and_dataframe(guess = None, result = default_result):
    """this function should be used as a decorator to add a fit function to Series (and DataFrame columns).
    
    Fit function:
     - The function should take a Series as first argument, and keywords for the variable arguments, 
    and return a vector of the same length as the Series.
     - The function should follow the naming convention func_SOMENAME.
     - It will then appear as anyseries.func_SOMENAME
    
    guess function: 
    - You can provide a guess function to find an initial guess for the parameters, 
    - the function should take a Series as argument and return the dictionary of keywords for the initial guess.
    - It will then appear as anyseries.func_SOMENAME_guess
     
    result: 
    - You can specify a custom class to store the result of the fit.
    - The class should inherit from the class default_result
    - The class object is appended to Series. 
    - The instances of the class, containing particular fit results are appended to the resulting DataFrame with the name: func_SOMENAME_res
    This is useful if extra calculations are commonly made using the fit results (see func_pdh for an exemple)"""
    
    
    def decorator(f):  
        if guess is not None:
            f.guess = guess
        f.result_class = result
        setattr(Series,f.__name__,f)
        setattr(Series,f.__name__ + "_guess",guess)
        
        setattr(DataFrame,f.__name__,f)
        #setattr(DataFrame,f.__name__ + "_guess",guess)
        
        return f
    return decorator


#===========================================================
#           lorentz
#===========================================================
def guess_peak(self):
    """ gives initial guess for amplitude, x_0, width of the peak in Y(X)
    return format : (FWHM,X0,a,offset)
    """
    iMax = self.argmax()

    x_0  = self.index[iMax]
    a    = self[iMax]

    HWHM_left = -1
    HWHM_right= -1
    offset = self.mean()
    a = a-offset
    for index in range(iMax,len(self)):
        if self[index]<=offset+a/2:
            FWHM = self.index[index] - x_0
        break
    if HWHM_right==-1:
        HWHM_right = self.index[index] - x_0
    for index in range(iMax,0,-1):
        if self[index]<=offset+a/2 :
            HWHM_left = x_0 - self.index[index]
            break
    if HWHM_left ==-1:
        HWHM_left = x_0 - self.index[index]

    FWHM = HWHM_left + HWHM_right
    if FWHM == 0:
        FWHM = (self.index[len(self)-1]-self.index[0])/10

    # convert a to area
    a = a*pi*FWHM/2
    return {"gamma":FWHM,"center":x_0,"ampl":a,"offset":offset}


@add_to_series_and_dataframe(guess = guess_peak)
def func_lorentz(self,center = 10.,gamma = 1.,ampl = 1.,offset = 0.):
    """computes a lorentzian"""
    X = array(self.index,dtype = float)
    return Series(ampl*gamma**2/((X-center)**2 + gamma**2) + offset,index = X)


@add_to_series_and_dataframe(guess = guess_peak)
def func_gauss(self,center = 10.,gamma = 1.,ampl = 1.,offset = 0.):
    """computes a lorentzian"""
    X = array(self.index,dtype = float)
    sigma=gamma/(2*math.sqrt(math.log(2)*2))
    return Series(ampl/(sigma*math.sqrt(2*pi))*exp(-(X-center)*(X-center)/(2*sigma**2))+offset)

    


#===========================================================
#           pdh
#===========================================================
def guess_pdh(ser):
    offset = ser.mean()
    std = ser.std()
    M = ser.index[ser.argmax()]
    m = ser.index[ser.argmin()]
    if M>m:
        ampl = -(ser.max()-ser.min())/2
    else:
        ampl = (ser.max()-ser.min())/2
    phi = 0
    center = (M+m)/2
    width = abs(M-m)
    
    
    ## upper sideband
    newser = ser[center+width*4:]
    Mup = newser.index[newser.argmax()]
    mup = newser.index[newser.argmin()]
    mod = (Mup+mup)/2 - center
    
    return {"center":center,"width":width,"mod":mod,"ampl":ampl,"offset": offset,"phi":phi}

 
@add_to_series_and_dataframe(guess = guess_pdh,result = result_pdh)
def func_pdh(self,center = 0.0,width = 1.0,mod = 100.0,ampl = 1.0,offset = 0.0,phi = 3.14):
    """computes a pdh lineshape"""
    X = array(self.index,dtype = float)
    Delta = X-center
#    phi = phi*pi/180.0
    f1 = 2*ampl*Delta*width*(mod**2)
    numer = ((Delta**2+width**2-mod**2)*cos(phi)-2*width*mod*sin(phi))
    denom = ((Delta**2+width**2)*(width**2+(Delta-mod)**2)*(width**2+(Delta+mod)**2))
    ret = offset + f1*numer/denom
    return Series(ret,index = X)


    