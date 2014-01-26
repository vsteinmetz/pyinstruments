"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
from curve import Curve, load

import os.path as osp
import numpy as np
from pylab import plot, show
from unittest import TestCase, main


SHOW_PLOTS = True
CURVE_FOLDER = osp.join(osp.split(__file__)[0], "test_curve")
log_file = __file__ + '.log'
with open(log_file, 'w'):
    pass

def print_and_log(*args):
    string = "".join([str(arg) for arg in args])
    print string
    with open(log_file, 'a') as f:
        f.write(string + '\n')
        
        
class TestFits(TestCase):
    def test_lorentz_complex(self):
        """
        Tests that a curve can be saved.
        """
        
        curve = load(osp.join(CURVE_FOLDER, "lorentz_complex1.h5"))
        f, c = curve.fit("lorentz_complex_sam")
        if SHOW_PLOTS:
            plot(np.real(curve.data), np.imag(curve.data))
            plot(np.real(f.getoversampledfitdata(5000)), np.imag(f.getoversampledfitdata(5000)))
            show()
        self.assertLess(f.sqerror, 1.4e-9)
        
    def test_lorentz_complex2(self):
        curve = load(osp.join(CURVE_FOLDER, "lorentz_complex2.h5"))
        f, c = curve.fit("lorentz_complex_sam")
        if SHOW_PLOTS:
            plot(np.real(curve.data), np.imag(curve.data))
            plot(np.real(f.getoversampledfitdata(5000)), np.imag(f.getoversampledfitdata(5000)))
            show()
        self.assertLess(f.sqerror, 8.2e-9)
        
    def test_lorentz_complex3(self):
        curve = load(osp.join(CURVE_FOLDER, "lorentz_complex3.h5"))
        f, c = curve.fit("lorentz_complex_sam")
        if SHOW_PLOTS:
            plot(np.real(curve.data), np.imag(curve.data))
            plot(np.real(c.data), np.imag(c.data))
            show()
        self.assertLess(f.sqerror, 4.4e-8)
        

if __name__=="__main__":
    main()