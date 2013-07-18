from numpy import *
import pandas
import func
import numbers
from collections import OrderedDict
import numpy







@monkey_add(pandas.Series)
def get_custom(self,name):
    try:
        return self.custom.__getattribute__(name)
    except AttributeError:
        self.customize()
        return dict()


    
    
    






import sys
if "remotePlotting" in sys.modules:
        from remotePlotting import plot as remote_plot
        pandas.Series.remote_plot = remote_plot
        