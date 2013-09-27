"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from pyinstruments.curvefindernew.models import CurveDB

from django.test import TestCase
import pandas
from datetime import datetime


class SimpleTest(TestCase):
    def test_curve_save(self):
        """
        Tests that a curve can be saved.
        """
        self.curve = CurveDB()
        self.curve.set_data(pandas.Series([1,4,6]))
        self.curve.save()
        
    def test_curve_filter_param_string(self):
        """
        Tests that a curve can be retrieved by a string param.
        """
        self.curve = CurveDB()
        self.curve.params['name'] = 'some_name'
        self.curve.set_data(pandas.Series([1,4,6]))
        self.curve.save()

        qs = CurveDB.objects.filter_param('name', value='some_name')
        self.assertTrue(self.curve in qs)
        
    def test_curve_filter_param_float(self):
        """
        Tests that a curve can be retrieved by a string param.
        """
        
        self.curve = CurveDB()
        self.curve.params['name'] = 'some_name'
        self.curve.params['Q'] = 1e6
        self.curve.set_data(pandas.Series([1,4,6]))
        self.curve.save()

        qs = CurveDB.objects.filter_param('Q', value=1e6)
        self.assertTrue(self.curve in qs)
        
    def test_curve_filter_param_float_lte(self):
        """
        Tests that a curve can be retrieved by a string param.
        """
        self.curve = CurveDB()
        self.curve.params['name'] = 'some_name'
        self.curve.params['Q'] = 1e6
        self.curve.set_data(pandas.Series([1,4,6]))
        self.curve.save()

        qs = CurveDB.objects.filter_param('Q', value__lte=1e7)
        self.assertTrue(self.curve in qs)
        qs = CurveDB.objects.filter_param('Q', value__gte=1e7)
        self.assertFalse(self.curve in qs)
        
    def test_curve_filter_param_boolean(self):
        """
        Tests that a curve can be retrieved by a string param.
        """
        self.curve = CurveDB()
        self.curve.params['name'] = 'some_name'
        self.curve.params['Q'] = 1e6
        self.curve.params['nice_curve'] = True
        self.curve.set_data(pandas.Series([1,4,6]))
        self.curve.save()

        qs = CurveDB.objects.filter_param('nice_curve', value=True)
        self.assertTrue(self.curve in qs)
        qs = CurveDB.objects.filter_param('nice_curve', value=False)
        self.assertFalse(self.curve in qs)
    
    def test_curve_filter_param_text(self):
        """
        Tests that a curve can be retrieved by a string param.
        """
        self.curve = CurveDB()
        self.curve.params['comment'] = 'bla bla bla'
        self.curve.params['Q'] = 1e6
        self.curve.params['nice_curve'] = True
        self.curve.set_data(pandas.Series([1,4,6]))
        self.curve.save()

        qs = CurveDB.objects.filter_param('comment', value__contains='bla')
        self.assertTrue(self.curve in qs)
        qs = CurveDB.objects.filter_param('nice_curve', value__contains='blo')
        self.assertFalse(self.curve in qs)
        
    def test_curve_filter_date(self):
        """
        Tests that a curve can be retrieved by a date.
        """
        self.curve = CurveDB()
        self.curve.params['comment'] = 'bla bla bla'
        self.curve.params['Q'] = 1e6
        self.curve.params['nice_curve'] = True
        self.curve.set_data(pandas.Series([1,4,6]))
        self.curve.save()

        qs = CurveDB.objects.filter_param('date', value__lte=datetime.now())
        self.assertTrue(self.curve in qs)
        qs = CurveDB.objects.filter_param('date', value__gte=datetime.now())
        self.assertFalse(self.curve in qs)
        
        
    def test_curve_filter_tag(self):
        """
        Tests that a curve can be retrieved by a date.
        """
        self.curve = CurveDB()
        self.curve.params['comment'] = 'bla bla bla'
        self.curve.params['Q'] = 1e6
        self.curve.params['nice_curve'] = True
        self.curve.tags.append('new_tag')
        self.curve.set_data(pandas.Series([1,4,6]))
        self.curve.save()
        self.curve.tags.append('other_tag')
        self.curve.save()
        self.curve2 = CurveDB()
        self.curve2.set_data(pandas.Series([1,4,6]))
        self.curve2.tags.append('new_tag')
        self.curve2.params['Q'] = 5e6
        self.curve2.save()

        qs = CurveDB.objects.filter_tag('new_tag')
        self.assertTrue(self.curve in qs)
        self.assertTrue(self.curve2 in qs)
        
        qs = CurveDB.objects.filter_tag('other_tag')
        self.assertTrue(self.curve in qs)
        self.assertFalse(self.curve2 in qs)
        
        qs = CurveDB.objects.filter_tag('new_tag').filter_tag("other_tag")
        self.assertTrue(self.curve in qs)
        self.assertFalse(self.curve2 in qs)
        
    def test_chained_filter(self):
        self.curve = CurveDB()
        self.curve.params['comment'] = 'bla bla bla'
        self.curve.params['Q'] = 1e6
        self.curve.params['nice_curve'] = True
        self.curve.tags.append('new_tag')
        self.curve.set_data(pandas.Series([1,4,6]))
        self.curve.save()
        self.curve.tags.append('other_tag')
        self.curve.save()
        self.curve2 = CurveDB()
        self.curve2.set_data(pandas.Series([1,4,6]))
        self.curve2.tags.append('new_tag')
        self.curve2.params['Q'] = 5e6
        self.curve2.save()
        
        qs = CurveDB.objects.filter_tag('new_tag').filter_param('Q', value__lte = 1e7)
        self.assertTrue(self.curve in qs)

        qs = CurveDB.objects.filter_tag('new_tag').filter_param('Q', value__gte = 1e7)
        self.assertFalse(self.curve in qs)
        
        qs = CurveDB.objects.filter_tag('new_tag').filter_tag('other_tag').filter_param('Q', value__lte = 1e7)
        self.assertTrue(self.curve in qs)
        self.assertFalse(self.curve2 in qs)