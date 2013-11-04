import pandas
import scipy.optimize
import numpy
import numpy as np
import collections
import math
from guiqwt.widgets.fit import FitParam, guifit

LAMBDA = 1.064e-6 #WTF !?

'''Here define the fitfunctions which shall appear in the fit context menu;
   Anything which starts with an underscore does not appear in that menu. 
   Default guessfunction has the same name as the fitfunction and starts with _guess'''
class FitFunctions(object):
    def sin(self, f, phi, scale, offset):
        x = self.x()
        return offset + scale*numpy.sin(2*numpy.pi*x*f + phi) 
    
    def _guesssin(self):
        fit_params = {'f': 0.25, 'phi':90, 'scale': 1.0, 'offset': 0.0}
        return fit_params
    
    def doublelorentz(self, x1, x2, bandwidth, scale, y0):
        x = self.x()
        return self.lorentz(scale=scale, x0=x1, y0=y0, bandwidth=bandwidth)+self.lorentz(scale=scale, x0=x2, y0=0, bandwidth=bandwidth)

        
    def _guessdoublelorentz(self):
        length = len(self.x())
        #estimate background from first and last 10% of datapoints in the trace
        bg = (self.data[:length/20].mean()+self.data[-length/20:].mean())/2.0
        
        magdata = abs(self.data-bg)
        argmax = magdata.argmax()
        _x1 = float(self.x()[argmax])
        magmax = magdata[_x1]
        max = self.data[_x1]
        
        for index, y in enumerate(magdata[_x1:]):
            if y<magmax/2:
                break
        bw = 2*abs(_x1 - self.data.index[argmax + index])
        bw_index = index
        
        
        ## Second peak search
        threshold_mag = magmax*0.7
        N_BW_AWAY = 10
        start = argmax + bw_index*N_BW_AWAY
        found = False
        for index, y in enumerate(magdata[start:]):
            if y>threshold_mag:
                found = True
                index = start + index
                break
        if not found:
            stop = argmax - bw_index*N_BW_AWAY
            found = False
            for index, y in enumerate(magdata[stop:0:-1]):
                if y>threshold_mag:
                    found = True
                    index = stop - index - 3*bw_index
                    break
                    
        next_peak_index_close = index
        next_peak_index = next_peak_index_close + magdata[next_peak_index_close:next_peak_index_close+3*bw_index].argmax()
        _x2 = float(self.x()[next_peak_index])
        #argmax = magdata.argmax()
        #x2 = float(self.x()[argmax])
        x1 = numpy.min([_x1, _x2])
        x2 = numpy.max([_x1, _x2])
        bw = abs(bw)
        
        fit_params = {'x1': x1, 'x2':x2, 'bandwidth': bw, 'scale': max-bg, 'y0': bg}
        return fit_params


    def dummy(self,x):
        return self.data
    
    def _guessdummy(self):
        return dict(dummyfix=0.0)
    
    '''defines w(z) for 1064nm wavelength for all units in meters'''
    def gaussianbeam(self,x0,w0):
        x=self.x()
        return w0*(((x-x0)**2/math.pi**2/w0**4*LAMBDA**2+1)**0.5)
    
    def _guessgaussianbeam(self):
        tempfit = Fit(data=self.data,func='linear_x0',maxiter=10)
        res = tempfit.getparams()
        params = dict(x0 = res['x0'], w0 = LAMBDA/math.pi/res['slope'])    
        return params
    
    '''linear function, fixed on ordinate axis'''
    def linear(self, y0, slope):
        x=self.x()
        return slope*x+y0

    def _guesslinear(self):
        max = self.data.max()
        min = self.data.min()
        slope = (max-min)/(self.x().max() - self.x().min())
        y0 = self.data.mean() - self.x().mean()*slope
        fit_params = {'y0': y0, 'slope': slope}
        return fit_params

    '''linear function, fixed on abscisse axis'''
    def linear_x0(self, x0, slope):
        x=self.x()
        return slope*(x-x0)

    def _guesslinear_x0(self):
        max = self.data.max()
        min = self.data.min()
        slope = (max-min)/(self.x().max() - self.x().min())
        x0 = self.x().mean() - self.data.mean()/slope
        fit_params = {'x0': x0, 'slope': slope}
        return fit_params

    def saturatedlinear(self,y0,slope):
        x=self.x()
        return 1/(1/(slope*x)+1/y0)

    def _guesssaturatedlinear(self):
        max = self.data.max()
        min = self.data.min()
        slope = (max-min)/(self.x().max()-self.x().min())
        y0 = self.data.mean() - self.x().mean()*slope
        fit_params = {'y0': min, 'slope': slope}
        return fit_params

    '''tempconductivity'''
    def exponential(self,scale,alpha):
        x=self.x()
        return scale*math.e**(-x*alpha)

    def _guessexponential(self):
        alpha=-1.0
        scale = 1#(self.data/(math.e**(self.x()*alpha))).mean()
        fit_params = {'scale': scale, 'alpha': alpha}
        return fit_params
    
    def steinharthart(self,A,B,C):
        x=self.x()
        return 1/(A+B*np.log(x)+C*np.log(x)**3)
    
    def _guesssteinharthart(self):
        max = self.data.max()
        imax=self.data.index[self.data.argmax()]
        min = self.data.min()
        imin=self.data.index[self.data.argmin()]
        imean=self.x()[int(math.floor(len(self.x())/2))]
        mean=self.data[imean]
        l1,l2,l3=math.log(imax),math.log(imin),math.log(imean)
        y1,y2,y3=1/max,1/min,1/mean
        g2=(y2-y1)/(l2-l1)
        g3  =(y3-y1)/(l3-l1)
        C=(g3-g2)/(l3-l2)/(l1+l2+l3)
        B=g2-C*(l1**2+l1*l2+l2**2)
        A=y1-(B -l1**2*C)*l1
        fit_params = {'A': A, 'B': B, 'C':C}
        return fit_params

    
            
    '''ringdown'''
    def ringdown(self,ringspersweeptime,gamma,y0,scale,overshoot):
        fitonhigh=True
        fitonlow=True
        dephase=0
        length = len(self.x())
        sweeptime = self.x().max()-self.x().min()
        ringtime = sweeptime/ringspersweeptime
        sweeps = int(math.ceil(ringspersweeptime))
        delta = ringtime*0.000
        result = self.data.copy()
        '''conversion from decay rate to decay slope on a log scale'''
        slope = gamma*2*math.pi*10*math.log10(math.e)
        for sweep in range(sweeps):
            high = self.data[(sweep+0.2*ringtime+delta):((sweep+0.5)*ringtime-delta)]
            low = self.data[((sweep+0.5)*ringtime+delta):((sweep+0.95)*ringtime-delta)]
            if fitonhigh:
                for i in high.index:
                    result[i] = scale+y0
            if fitonlow and len(low)>0:
                ringstart = min(low.index)
                for i in low.index:
                    #result[i]=max([y0,y0+scale+overshoot-slope*(i-ringstart)])
                    result[i]=math.log10(10**y0+10**(y0+scale+overshoot-abs(slope)*(i-ringstart)))
        return numpy.array(result.values,dtype=float)

    def _guessringdown(self):
        ringspersweeptime = 1.0
        length = len(self.x())
        sweeptime = self.x().max()-self.x().min()
        ringtime = sweeptime/ringspersweeptime
        sweeps = int(math.ceil(ringspersweeptime))
        delta = ringtime*0.000
        highsum=0
        highs=0
        lows=0
        lowsum=0
        for sweep in range(sweeps):
            high = self.data[(sweep+0.25*ringtime+delta):((sweep+0.5)*ringtime-delta)]
            low = self.data[((sweep+0.80)*ringtime+delta):((sweep+0.95)*ringtime-delta)]
            for i in high.index:
                highsum+=self.data[i]
                highs+=1
            for i in low.index:
                lowsum+=self.data[i]
                lows+=1
        y0=(lowsum/lows)
        scale=(highsum/highs)-y0
        firstlows = self.data[0.505*ringtime+delta:(0.505)*ringtime+delta+sweeptime/length*math.ceil(length/ringspersweeptime/2/1000)]
        tempfit = Fit(data = firstlows, func = 'linear', \
                      autoguessfunction = '', \
                      fixed_params = {}, \
                      manualguess_params = {}, \
                      verbosemode = False, maxiter = 10)
        '''tempfit_params holds the parameters for the guess now, '''
        '''which should be nearly optimal already'''
        tempfitparams = tempfit.getparams()
        gamma = abs(tempfitparams['slope'])/(2*math.pi*10*math.log10(math.e))
        overshoot = tempfitparams['y0']+tempfitparams['slope']*min(firstlows.index)-scale-y0
        fit_params = dict(ringspersweeptime=ringspersweeptime,gamma=gamma,y0=y0,\
                          scale=scale,overshoot=overshoot)
        self.fixed_params = dict(ringspersweeptime=ringspersweeptime,y0=y0,scale=scale) 
        return fit_params

    def _guessringdown_log(self):
        ringspersweeptime = 1.0
        length = len(self.x())
        sweeptime = self.x().max()-self.x().min()
        ringtime = sweeptime/ringspersweeptime
        sweeps = int(math.ceil(ringspersweeptime))
        delta = ringtime*0.000
        highsum=0
        highs=0
        lows=0
        lowsum=0
        for sweep in range(sweeps):
            high = self.data[(sweep+0.2*ringtime+delta):((sweep+0.5)*ringtime-delta)]
            low = self.data[((sweep+0.80)*ringtime+delta):((sweep+0.95)*ringtime-delta)]
            for i in high.index:
                highsum+=10**self.data[i]
                highs+=1
            for i in low.index:
                lowsum+=self.data[i]
                lows+=1
        y0=(lowsum/lows)
        scale=math.log10(highsum/highs)-y0
        firstlows = self.data[0.5*ringtime+delta:(0.5)*ringtime+delta+sweeptime/length*math.ceil(length/ringspersweeptime/2/1000)]
        tempfit = Fit(data = firstlows, func = 'linear', \
                      autoguessfunction = '', \
                      fixed_params = {}, \
                      manualguess_params = {}, \
                      verbosemode = False, maxiter = 10)
        '''tempfit_params holds the parameters for the guess now, '''
        '''which should be nearly optimal already'''
        tempfitparams = tempfit.getparams()
        gamma = abs(tempfitparams['slope'])/(2*math.pi*10*math.log10(math.e))
        overshoot = tempfitparams['y0']+tempfitparams['slope']*min(firstlows.index)-scale-y0
        fit_params = dict(ringspersweeptime=ringspersweeptime,gamma=gamma,y0=y0,\
                          scale=scale,overshoot=overshoot)
        self.fixed_params = dict(ringspersweeptime=ringspersweeptime,y0=y0,scale=scale) 
                                 #overshoot=overshoot)
        return fit_params


    def _guessringdown_linear(self):
    #def _guessringdown_linear(self):
        ringspersweeptime = 1.0
        length = len(self.x())
        sweeptime = self.x().max()-self.x().min()
        ringtime = sweeptime/ringspersweeptime
        sweeps = int(math.ceil(ringspersweeptime))
        delta = ringtime*0.000
        highsum=0
        highs=0
        lows=0
        lowsum=0
        for sweep in range(sweeps):
            high = self.data[(sweep+0.2*ringtime+delta):((sweep+0.5)*ringtime-delta)]
            low = self.data[((sweep+0.80)*ringtime+delta):((sweep+0.95)*ringtime-delta)]
            for i in high.index:
                highsum+=10**self.data[i]
                highs+=1
            for i in low.index:
                lowsum+=10**self.data[i]
                lows+=1
        y0=math.log10(lowsum/lows)
        scale=math.log10(highsum/highs)-y0
        
        firstlows = self.data[0.5*ringtime+delta:(0.5)*ringtime+delta+sweeptime/length*math.ceil(length/ringspersweeptime/2/1000)]
        tempfit = Fit(data = firstlows, func = 'linear', \
                      autoguessfunction = '', \
                      fixed_params = {}, \
                      manualguess_params = {}, \
                      verbosemode = False, maxiter = 10)
        '''tempfit_params holds the parameters for the guess now, '''
        '''which should be nearly optimal already'''
        tempfitparams = tempfit.getparams()
        gamma = abs(tempfitparams['slope'])/(2*math.pi*10*math.log10(math.e))
        overshoot = tempfitparams['y0']+tempfitparams['slope']*min(firstlows.index)-scale-y0
        fit_params = dict(ringspersweeptime=ringspersweeptime,gamma=gamma,y0=y0,\
                          scale=scale,overshoot=overshoot)
        self.fixed_params = dict(ringspersweeptime=ringspersweeptime,y0=y0,scale=scale,\
                                 overshoot=overshoot)
        return fit_params

    def _guessringdown_old(self):
        ringspersweeptime = 1.0
        y0 = self.data.min()
        scale = self.data.max()-y0
        overshoot = 0.0
        sweeptime = self.x().max()-self.x().min()
        ringtime = sweeptime/ringspersweeptime
        slope = (scale+overshoot)/ringtime/100.0
        gamma = slope/(2*10*math.pi*math.log10(math.e))
        fit_params = dict(ringspersweeptime=ringspersweeptime,gamma=gamma,y0=y0,\
                          scale=scale,overshoot=overshoot)
        return fit_params
 
    #simple lorentzian in linear scale
    def lorentz(self, scale, x0, y0, bandwidth):
        x = self.x()
        return scale/(1+((x-x0)/bandwidth)*((x-x0)/bandwidth))+y0

    def _guesslorentz_simple(self):
        x0 = float(self.x()[self.data.argmax()])
        max = self.data.max()
        min = self.data.min()
        bw = 0.1*(self.x().max() - self.x().min())
        fit_params = {'x0': x0, 'y0': min, 'scale': max-min, 'bandwidth': bw}
        return fit_params

    def _guesslorentz(self):
        length = len(self.x())
        #estimate background from first and last 10% of datapoints in the trace
        bg = (self.data[:length/10].mean()+self.data[-length/10:].mean())/2.0
        magdata = abs(self.data-bg)
        x0 = float(self.x()[magdata.argmax()])
        magmax=magdata[x0]
        max=self.data[x0]
        bw = magdata.sum()/magmax*(self.x().max()-self.x().min())/length
        fit_params = {'x0': x0, 'y0': bg, 'scale': max-bg, 'bandwidth': bw}
        return fit_params

    
    def lorentz_log(self, scale, x0, y0, bandwidth):
        """logarithmic lorentz, typ. SA traces"""
        x = self.x()
        return 10*log10(scale/(1+((x-x0)/bandwidth)*((x-x0)/bandwidth)))+y0

    def _guesslorentz_log(self):
        length = len(self.x())
        '''estimate background from first and last 10% of datapoints in the trace'''
        data = 10**(self.data/10.0)
        bg = ((data[:length/10].mean()+data[-length/10:].mean())/2.0)
        magdata = abs(data-bg)
        x0 = float(self.x()[magdata.argmax()])
        magmax=self.magdata[x0]
        max=data[x0]
        bw = magdata.sum()/magmax*(self.x().max()-self.x().min())/length
        fit_params = {'x0': x0, 'y0': bg, 'scale': max-bg, 'bandwidth': bw}
        return fit_params

    '''complex lorentz in linear scale, typically from NA traces'''
    def lorentz_complex(self, bandwidth, scale_re, scale_im, x0, y0_re,y0_im):
        x = self.x()
        return (scale_re+scale_im*1j)/(1+(1j*(x-x0)/bandwidth))+y0_re+y0_im*1j
    
    def _guesslorentz_complex(self):
        length = len(self.x())
        '''estimate background from first and last 10% of datapoints in the trace'''
        bg = (self.data[:length/10].mean()+self.data[-length/10:].mean())/2.0
        magdata = (self.data-bg)*numpy.conjugate(self.data-bg)
        x0 = float(self.x()[magdata.argmax()])
        magmax=magdata[x0]
        max=self.data[x0]
        bw = magdata.sum()/magmax*(self.x().max()-self.x().min())/length
        fit_params = dict(bandwidth=bw,scale_re=real(max),scale_im=imag(max),
                          x0=x0,y0_re=real(bg),y0_im=imag(bg))
        return 

    '''lorentz with symmetric sidebands, typ. absorption/transmission dips of cavities'''
    def lorentzSB(self, scale, x0, y0, bandwidth, SBwidth, SBscale):
        x = self.x()
        return y0 + scale*(1/(1+((x-x0)/bandwidth)*((x-x0)/bandwidth))+\
                SBscale/(1+((x-x0-SBwidth)/bandwidth)**2)+\
                SBscale/(1+((x-x0+SBwidth)/bandwidth)**2))


    def _guesslorentzSB(self):
        from curve import Curve
        cu = Curve()
        cu.set_data(self.data)
        res, lor = cu.fit('lorentz')
        magdata = lor.data.abs()
        scale = numpy.sign(lor.params['scale'])*(magdata.max() - abs(lor.params['y0']))
        res, lor = cu.fit('lorentz', fixed_params={'x0':lor.params['x0'], 'bandwidth':0.7*lor.params['bandwidth'], 'scale':scale})
        diff = numpy.sign(lor.params['scale'])*(cu.data - lor.data)*self.lorentz(-1.0, lor.params['x0'], 1.0, lor.params['bandwidth'])
        upper_half = diff[lor.params['x0']:]
        index_up = upper_half.argmax()
        scale_up = upper_half[index_up]
        x_up = upper_half.index[index_up]
        
        lower_half = diff[:lor.params['x0']]
        index_lo = lower_half.argmax()
        scale_lo = lower_half[index_lo]
        x_lo = lower_half.index[index_lo]
        

#        replacement = {'bandwidth': fit_params['bandwidth']/2.0,\
#                       'SBwidth': fit_params['bandwidth']*1.1, 'SBscale' : 0.3}
        return {'scale' : lor.params['scale'],
                'x0' : lor.params['x0'],
                'y0' : lor.params['y0'],
                'bandwidth' : lor.params['bandwidth'],
                'SBwidth' : (x_up - x_lo)/2,
                'SBscale' : 1./lor.params['scale']*(scale_up + scale_lo)/2}

    def _guesslorentzSB_simple(self):
        x0 = float(self.x()[self.data.argmax()])
        max = self.data.max()
        min = self.data.min()
        bw = 0.1*(self.x().max() - self.x().min())
        fit_params = {'x0': x0, 'y0': min, 'scale': max-min, 'bandwidth': bw, \
                      'SBwidth': 1.8*bw, 'SBscale' : 0.3}
        return fit_params

    def _guesslorentzSBfromlorentzOld_tobedeleted(self):
        self.comment("Estimating first fit parameters from simple lorentz fit")
        tempfit = Fit(data = self.data, func = 'lorentz', \
                      autoguessfunction = '', fixed_params = self.fixed_params, \
                      manualguess_params = self.manualguess_params, \
                      verbosemode = self.verbosemode, maxiter = 20)
        tempfit_params = tempfit.getparams()
        self.comment("")
        self.comment("Estimating remaining fit parameters from lorentzSB fit with fixed previously determined parameters")
        tempfit = Fit(data = self.data, func = 'lorentzSB', \
                      autoguessfunction = '', fixed_params = tempfit_params, \
                      manualguess_params = self.manualguess_params, \
                      verbosemode = self.verbosemode, maxiter = 20)
        fit_params = tempfit.getparams()
        return fit_params

    def _guesslorentzSBguessfixfromlorentzSB(self):
        '''use the more evolved guess from guesslorentzSBfixfromlorentz'''
        self.comment("perform guesslorentzSBfixfromlorentz...")
        tempfit = Fit(data = self.data, func = 'lorentzSB', \
                      autoguessfunction = '_guesslorentzSBfixfromlorentz', \
                      fixed_params = self.fixed_params, \
                      manualguess_params = self.manualguess_params, \
                      verbosemode = self.verbosemode, maxiter = 15)
        '''tempfit_params holds the parameters for the guess now, '''
        '''which should be nearly optimal already'''
        fit_params = tempfit.getparams()
        '''if fixed_params are defined at the fit function call, '''
        '''they automatically found their way into fit_params'''
        self.fixed_params['bandwidth']=fit_params['bandwidth']
        self.fixed_params['SBwidth']=fit_params['SBwidth']
        return fit_params 

    def _guesslorentzSBguessfromlorentzSB(self):
        '''use the more evolved guess from guesslorentzSBfixfromlorentz'''
        self.comment("perform guesslorentzSBfixfromlorentz...")
        tempfit = Fit(data = self.data, func = 'lorentzSB', \
                      autoguessfunction = '_guesslorentzSBfixfromlorentz', \
                      fixed_params = self.fixed_params, \
                      manualguess_params = self.manualguess_params, \
                      verbosemode = self.verbosemode, maxiter = 15)
        '''tempfit_params holds the parameters for the guess now, '''
        '''which should be nearly optimal already'''
        fit_params = tempfit.getparams()
#        '''if fixed_params are defined at the fit function call, '''
#        '''they automatically found their way into fit_params'''
#        self.fixed_params['bandwidth']=fit_params['bandwidth']
#        self.fixed_params['SBwidth']=fit_params['SBwidth']
        return fit_params 

    def _guesslorentzSBfixfromlorentz(self):
        self.comment("Estimating first fit parameters from simple lorentz fit")
        tempfit = Fit(data = self.data, func = 'lorentz', \
                      autoguessfunction = '_guesslorentz', \
                      fixed_params = self.fixed_params, \
                      manualguess_params = self.manualguess_params, \
                      verbosemode = self.verbosemode, maxiter = 15)
        '''tempfit_params holds the parameters to keep fixed'''
        '''bwguess is the guess for the bandwidth''' 
        tempfit_params = tempfit.getparams()
        bwguess = tempfit_params.pop('bandwidth')
        '''however, the manually fixed parameters are left unchanged'''
        tempfit_params.update(self.fixed_params)
        self.fixed_params = tempfit_params.copy()
        '''construct the remaining guess parameters and return them'''
        fitparams = collections.OrderedDict({'bandwidth': bwguess/2., \
                            'SBwidth': 1.1 * bwguess, 'SBscale' : 0.25})
        self.comment("Prefit for parameter guess obtained the following results: ")
        self.comment("Fixed: "+str(self.fixed_params))
        self.comment("Manual: "+str(self.manualguess_params))
        self.comment("Automatic: "+str(fitparams))
        return fitparams



class Fit(FitFunctions):
    def __init__(self, data, func, fixed_params={}, manualguess_params={},
                 autoguessfunction='' , verbosemode=True, maxiter=1000, 
                 errfn='error_vector', autofit=True, graphicalfit=False):
                 #errfn='squareerror_dbweighted'):
        self._x_npy = None
        self._y_npy = None
        self.autofit = autofit
        self.autofitgraphical = graphicalfit
        self.data = data
        self.sqerror = float('nan')
        self.verbosemode = verbosemode
        self.stepcount = 0
        self.maxiter = maxiter
        self.fitfunctions = FitFunctions()
        self.commentstring = ''
        self.fixed_params = collections.OrderedDict(fixed_params)
        self.manualguess_params = collections.OrderedDict(manualguess_params)
        
        # dynamically choose the fit function according to the passed func string
        self.func = func
        self.fn = self.__getattribute__(self.func)
        
        # define the error function to be optimised
        self.errfn = errfn
        self.fn_error = self.__getattribute__(self.errfn)
        
        # choose automatic guess function for starting parameter estimation
        self.autoguessfunction = autoguessfunction
        if self.autoguessfunction =='':
            self.fn_guess = self.__getattribute__('_guess'+self.func)
        else:
            self.fn_guess = self.__getattribute__(self.autoguessfunction)
        
        # guess unfixed parameters
        self.autoguess_params = self.fn_guess()
        
        # take all parameters passed during the function call as fixed, 
        # and assume that others have to be guessed
        # fixed_params are invariably fixed
        # manualguess_params have been guessed manually
        # the remaining autoguess_params were guessed by the guess function
        self.fit_params = collections.OrderedDict()
        for key in self.fn.func_code.co_varnames[1:self.fn.func_code.co_argcount]:
            if key in self.fixed_params:
                pass
            elif key in self.manualguess_params:
                self.fit_params[key] = self.manualguess_params[key]
            else: 
                self.fit_params[key] = self.autoguess_params[key]

        self.comment("Square sum of data: " + str((self.data**2).sum()))
        self.comment("Calling fit function with following guesses: ")
        self.comment(str(dict(self.getparams())))
        
        if self.autofit:
        # the parameters in fixed_params and fit_params are now ready for the fit 
            if not self.autofitgraphical:
                res = self.fit()
                self.comment("Return of fit optimisation function: ")
                self.comment(str(res))
            else:
                res = self.graphicalfit()
                self.comment("Return of fit optimisation function: ")
                self.comment(str(res))
                
    def graphicalfit(self):
        #SHOW = True # Show test in GUI-based test launcher
        x=self.x()
        y=self.y()
        
        def fitfn(x, params):
            #ignore the x
            for index, key in enumerate(self.fit_params):
                self.fit_params[key] = float(params[index])
                res = self.fn(**self.getparams())  
                if len(x)!=len(self.x()):
                    s = pandas.Series(res, index=self.x())
                    res = s[x].values   
            return res
        
        self.graphical_params=list()
        for index, key in enumerate(self.fit_params):
                fp=FitParam(key,self.fit_params[key],0.001*abs(self.fit_params[key]),10.0*abs(self.fit_params[key]),logscale=False,steps=2000,format='%.8f')
                self.graphical_params.append(fp)
        values = guifit(x, y, fitfn, self.graphical_params, xlabel="x-axis", ylabel="y-axis")
        if values is None:
            self.gfit_concluded = False
        else:
            self.gfit_concluded = True
            
        self.comment("Graphical fit finished with the following values: ")        
        self.comment(values)
        self.comment([param.value for param in self.graphical_params])
        self.sqerror = self.getsqerror() 
        self.comment("Fit completed with sqerror = " + str(self.sqerror))
        self.comment("Obtained parameter values: ")
        self.comment(dict(self.getparams()))
        # evaluate the performed fit in fitdata
        self.fitdata = pandas.Series(data = self.fn(**self.getparams()), index = self.x(), \
                            name = 'fitfunction: '+ self.func)    
        return values
 
 
    def error_vector(self, args):
        # unfold the list of parameters back into the dictionary 
        for index, key in enumerate(self.fit_params):
            self.fit_params[key] = float(args[index])
        
        # calculate the square error
        self.sqerror_vector = self.fn(**self.getparams())-self.data.values
        #print "params: ", args
        #print "sqerr: ", self.sqerror
        return self.sqerror_vector
    # define function for fit parameter optimization, usually simple leastsquares method
    def squareerror_old(self, args):
        # unfold the list of parameters back into the dictionary 
        for index, key in enumerate(self.fit_params):
            self.fit_params[key] = float(args[index])
        
        # calculate the square error
        self.sqerror = float(((self.fn(**self.getparams())-self.data.values)**2).mean())
        
        #print "params: ", args
        #print "sqerr: ", self.sqerror
        return self.sqerror

    def squareerror_dbweighted(self, kwds):
        # unfold the list of parameters back into the dictionary 
        for index, key in enumerate(self.fit_params):
            self.fit_params[key] = float(kwds[index])
        # calculate the square error
        sqtable = abs(self.fn(**self.getparams())-self.data.values)/10.0
        wsqtable = 10**sqtable
        #wsqtable = sqtable * 10**(self.data.values/10.0)
        self.sqerror = float(wsqtable.mean())
        return self.sqerror
        
    def getparams(self):
        params = self.fit_params.copy()
        params.update(self.fixed_params)
        return params
    
#get the square error for actual parameters
    def getsqerror(self):
        return self.squareerror_old(self.fit_params.values())
    
    def comment(self, string):
        if self.verbosemode is True:
            print string
        self.commentstring += str(string) + "\r\n"

    def x(self):
        if self._x_npy is None:
            self._x_npy = numpy.array(self.data.index,dtype=float)
        return  self._x_npy
    
    def y(self):
        if self._y_npy is None:
            self._y_npy = numpy.array(self.data.values,dtype=float)
        return self._y_npy
    
    
    def fit(self):
        res = scipy.optimize.leastsq(func=self.fn_error,
                                     x0=self.fit_params.values(),
                                     xtol=1e-4,
                                     ftol=1e-4,
                                     gtol=1e-4)
        self.sqerror = self.getsqerror() 
        self.comment("Fit completed with sqerror = " + str(self.sqerror))
        self.comment("Obtained parameter values: ")
        self.comment(dict(self.getparams()))
        # evaluate the performed fit in fitdata
        self.fitdata = pandas.Series(data=self.fn(**self.getparams()), index=self.x(),
                            name='fitfunction: '+ self.func )
        return res
    
    
    def fit_old(self):
        # by default use scipy standard function for optimization
        res = scipy.optimize.minimize(\
                            fun = self.fn_error,
                            # objective function to 
                            x0 = self.fit_params.values(), 
                            # ndarray of initial guess
                            args=(),
                            # extra args for objective function
                            method='BFGS', # default choice
                            jac=False,  # estimate jacobian numerically
                            hess=None,  # hessian also numerically estimated
                            hessp=None,  # hessian times vector also numerically estimated
                            bounds=None, # no bounds
                            constraints=(), # no constrains
                            tol=None, # tolerance for termination
                            callback=self.printstatus, #N'one' optional function call after each iteration
                            #more at scipy.optimize.show_options('minimize')
                            options={'maxiter': self.maxiter, 'disp': self.verbosemode, 'gtol':1e-4}) 
                            # max iterations and verbose mode
        
        self.sqerror = self.getsqerror() 
        self.comment("Fit completed with sqerror = " + str(self.sqerror))
        self.comment("Obtained parameter values: ")
        self.comment(dict(self.getparams()))
        # evaluate the performed fit in fitdata
        self.fitdata = pandas.Series(data=self.fn(**self.getparams()), index=self.x(),
                            name='fitfunction: '+ self.func )
        return res
    
    def getoversampledfitdata(self,numbersamples):
        datasafe = self.data
        maxindex = self.x().max()
        print maxindex
        minindex = self.x().min()
        print minindex
        newindex = numpy.array(numpy.linspace(minindex,maxindex,numbersamples),dtype=float)
        self.data = pandas.Series(data=newindex,index=newindex)
        self.fitdata = pandas.Series(data = self.fn(**self.getparams()), index = self.x(), \
                       name = 'fitfunction: '+ self.func )
        self.data = datasafe
        return self.fitdata

    
    def printstatus(self,dummy):
        self.stepcount += 1
        self.comment("Step "+str(self.stepcount) + " with sqerror = " + str(self.sqerror)) 
        self.comment(dict(self.getparams()))
        self.comment("dummy: " + str(dummy))

