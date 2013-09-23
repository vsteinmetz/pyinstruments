import pandas
import scipy.optimize
import numpy
import collections

class Fit(object):
    def __init__(self, data, func, fixed_params = {}, manualguess_params = {}, autoguessfunction = '' , verbosemode = True):
        self.data = data
        self.sqerror = float('nan')
        self.verbosemode = verbosemode
        
        # dynamically choose the fit function according to the passed func string
        self.func = func
        self.fn = self.__getattribute__(self.func)
        
        # choose automatic guess function for starting parameter estimation
        self.autoguessfunction = autoguessfunction
        if self.autoguessfunction =='':
            self.fn_guess = self.__getattribute__(self.func + '_guess')
        else:
            self.fn_guess = self.__getattribute__(self.guess)
        
        # guess unfixed parameters
        self.autoguess_params = self.fn_guess()
        
        # take all parameters passed during the function call as fixed, 
        # and assume that others have to be guessed
        # fixed_params are invariably fixed
        # manualguess_params have been guessed manually
        # the remaining autoguess_params were guessed by the guess function
        self.fixed_params = collections.OrderedDict(fixed_params)
        self.manualguess_params = manualguess_params
        self.fit_params = collections.OrderedDict()
        for key in self.fn.func_code.co_varnames[1:self.fn.func_code.co_argcount]:
            if key in self.fixed_params:
                pass
            elif key in self.manualguess_params:
                self.fit_params[key] = self.manualguess_params[key]
            else: 
                self.fit_params[key] = self.autoguess_params[key]
        
        # the parameters in fixed_params and fit_params are now ready for the fit 
        self.fit()
        
        # evaluate the performed fit
        self.fitdata = pandas.Series(data = self.fn(**self.getparams()), index = self.x(), \
                            name = 'fitfunction: '+ self.func )
        
        
    def getparams(self):
        params = self.fit_params
        params.update(self.fixed_params)
        return params
    
#get the square error for actual parameters
    def sqerror(self):
        return self.squareerror(self.fit_params.values())
    
# define function for fit parameter optimisation, usually simple leastsquares method
    def squareerror(self, kwds):
        # unfold the list of parameters back into the dictionary 
        for index, key in enumerate(self.fit_params):
            self.fit_params[key] = float(kwds[index])
        # calculate the square error
        self.sqerror = float(((self.fn(**self.getparams())-self.data.values)**2).sum())
        return self.sqerror
        
    def x(self):
        return numpy.array(self.data.index,dtype=float)

    def fit(self):
        # by default use scipy standard function for optimization
        res = scipy.optimize.minimize(\
                            fun = self.squareerror,
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
                            tol=1e-5, # tolerance for termination
                            callback=None, # optional function call after each iteration
                            #more at scipy.optimize.show_options('minimize')
                            options={'maxiter': 10000, 'disp': self.verbosemode}) # max 1000 iterations and verbose mode on 
        if self.verbosemode is True:
            print "Fit completed with sqerror = " + str(self.sqerror)
            print "Obtained parameter values: "
            print dict(self.getparams())
        return 0
        
    def lorentz(self, scale, x0, y0, bandwidth):
        x = self.x()
        return scale/(1+((x-x0)/bandwidth)*((x-x0)/bandwidth))+y0
    
    def lorentz_guess(self):
        x0 = float(self.data.argmax())
        max = self.data.max()
        min = self.data.min()
        bw = 0.1*(self.x().max() - self.x().min())
        fit_params = {'x0': x0, 'y0': min, 'scale': max-min, 'bandwidth': bw}
        return fit_params
    
    def linear(self, x0, slope):
        x=self.x()
        return slope * (x-x0)

    def linear_guess(self):
        max = self.data.max()
        min = self.data.min()
        slope = (max-min)/(self.x().max() - self.x().min())
        x0 = self.x().mean() - self.data.mean()/slope
        fit_params = {'x0': x0, 'slope': slope}
        return fit_params
    
    def lorentzSB(self,x = 0):
        pass
    