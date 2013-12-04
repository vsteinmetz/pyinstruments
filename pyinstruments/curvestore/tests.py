"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from pyinstruments.curvestore.models import CurveDB, Tag, ParamColumn, clear_unused_columns

from django.test import TestCase
import pandas
from datetime import datetime
import time

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
     
     
    def test_remove_tag(self):
        """
        Tests that a curve can be retrieved by a date.
        """
        self.curve = CurveDB()
        self.curve.set_data(pandas.Series([1,4,6]))
        self.curve.save()
        self.curve.tags.append('other_tag')
        self.curve.save()
        qs = CurveDB.objects.filter_tag('other_tag')
        self.assertTrue(self.curve in qs)
        self.curve.tags.pop(0)
        self.curve.save()
        curve = CurveDB.objects.get(id=self.curve.id)
        self.assertTrue("other_tag" not in curve.tags)
        
       
    def test_rename_tag(self):
        """
        Tests that a curve can be retrieved by a date.
        """
        self.curve = CurveDB()
        self.curve.set_data(pandas.Series([1,4,6]))
        self.curve.save()
        self.curve.tags.append('other_tag')
        self.curve.save()
        
        tag = Tag.objects.get(name='other_tag')
        tag.name = 'brand_new_name'
        tag.save()
        curve = CurveDB.objects.get(id=self.curve.id)
        
        self.assertTrue(curve.tags == ['brand_new_name'])
        
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
        
        
from pyinstruments.curvestore.models import Tag, top_level_tags

class TestTagModel(TestCase):
    def test_top_level_tag(self):
        """
        
        """
        self.tag = Tag(name='tag1')
        self.tag.save()
        self.tag2 = Tag(name='tag2')
        self.tag2.save()

        self.assertTrue(top_level_tags()[1].name == 'tag2')



    def test_childs(self):
        tag, cr = Tag.objects.get_or_create(name='tag1')
        tag2, cr = Tag.objects.get_or_create(name='tag1/tag2')    
        tag3, cr = Tag.objects.get_or_create(name='tag1/tag3')

        self.assertTrue(tag.childs()[1].name == 'tag1/tag3')
        self.assertTrue(tag.childs()[1].shortname == 'tag3')

    def test_move(self):
        tag, cr = Tag.objects.get_or_create(name='tag1')
        tag2, cr = Tag.objects.get_or_create(name='tag1/tag2')    
        tag3, cr = Tag.objects.get_or_create(name='tag1/tag3')  
        tag4, cr = Tag.objects.get_or_create(name='tag1/tag3/tag4')

        tag3.move(tag2.name)

        self.assertTrue(len(tag.childs())==1)
        self.assertTrue(tag.childs()[0].shortname == 'tag2')
        self.assertTrue(tag.childs()[0].childs()[0].shortname == 'tag3')
        self.assertTrue(tag.childs()[0].childs()[0].childs()[0].shortname == 'tag4')

    def test_move_to_root(self):
        tag, cr = Tag.objects.get_or_create(name='tag1')
        tag2, cr = Tag.objects.get_or_create(name='tag1/tag2')    
        tag3, cr = Tag.objects.get_or_create(name='tag1/tag3')  
        tag4, cr = Tag.objects.get_or_create(name='tag1/tag3/tag4')

        tag3.move("")

        self.assertTrue(len(top_level_tags())==2)
        self.assertTrue(len(tag.childs())==1)
        
        self.assertTrue(top_level_tags()[1].shortname == 'tag3')
        self.assertTrue(top_level_tags()[1].childs()[0].shortname == 'tag4')
                


from pyinstruments.curvestore.tags import HierarchicalTag, ROOT
from pyinstruments.curvestore.tag_widget import oldest_ancestors

class TestHierarchicalTag(TestCase):
    def test_child(self):
        ch = HierarchicalTag('tag1', parent=ROOT)
        ch2 = HierarchicalTag('tag2', parent=ROOT)
        ch3 = HierarchicalTag('tag3', parent=ch2)
        self.assertTrue(ROOT.children[0].name=='tag1')
        self.assertTrue(ROOT.children[1].name=='tag2')
        self.assertTrue(ROOT.children[1].children[0].name=='tag3')
    
    def test_remove(self):
        ROOT.remove_all_children()
        ch = HierarchicalTag('tag1', parent=ROOT)
        ch2 = HierarchicalTag('tag2', parent=ROOT)
        ch3 = HierarchicalTag('tag3', parent=ch2)
        ch2.remove_all_children()
        
    def test_fullname(self):
        ch = HierarchicalTag('tag1', parent=ROOT)
        ch2 = HierarchicalTag('tag2', parent=ROOT)
        ch3 = HierarchicalTag('tag3', parent=ch2)
        self.assertTrue(ch3.fullname=='tag2/tag3')
        self.assertTrue(ch2.fullname=='tag2')
        
    def test_oldest_ancestors(self):
        ch = HierarchicalTag('tag1', parent=ROOT)
        ch2 = HierarchicalTag('tag2', parent=ROOT)
        ch3 = HierarchicalTag('tag3', parent=ch2)
        ch4 = HierarchicalTag('tag4', parent=ROOT)
        
        self.assertTrue(len(oldest_ancestors((ch2, ch3)))==1)
        self.assertTrue(oldest_ancestors((ch2, ch3))[0]==ch2)   
        self.assertTrue(len(oldest_ancestors((ch2, ch3, ch4)))==2)        
        self.assertTrue(ch4 in oldest_ancestors((ch2, ch3, ch4)))  
        self.assertTrue(ch2 in oldest_ancestors((ch2, ch3, ch4)))     
      

        
class TestHierarchicalTagFromModelTag(TestCase):
    def test_child(self):
        ROOT.remove_all_children()
        tag, cr = Tag.objects.get_or_create(name='tag')
        tag2, cr = Tag.objects.get_or_create(name='tag1/tag2')    
        tag3, cr = Tag.objects.get_or_create(name='tag1/tag3')
        ROOT.build_children_from_model()
        self.assertTrue(ROOT.children[1].children[0].name=='tag2')
        
""" 
class TestTagsGui(TestCase):
    def test_child(self):
        tag, cr = Tag.objects.get_or_create(name='tag')
        tag, cr = Tag.objects.get_or_create(name='tag1')
        tag2, cr = Tag.objects.get_or_create(name='tag1/tag2')    
        tag3, cr = Tag.objects.get_or_create(name='tag1/tag3')
        ROOT.build_children_from_model()
        from pyinstruments.curvestore.tag_widget import TagTreeView
        from guidata import qapplication
        #app = qapplication()
        t = TagTreeView()
        #t.show()
        #app.exec_()
        
        ROOT.build_children_from_model()
        #app = qapplication()
        t = TagTreeView()
        #t.show()
        #app.exec_()
"""

class TestParams(TestCase):
    def test_insert_param(self):
        curve = CurveDB()
        curve.set_data(pandas.Series([1,4,6]))
        curve.save()
        
        for i in range(100):
            curve.params['coucou' + str(i)] = i
        curve.save()
        cu = CurveDB.objects.get(id=curve.id)
        self.assertTrue(cu.params['coucou12']==12)
        
        cu.params['coucou12'] = 45.
        cu.save()
        cu2 = CurveDB.objects.get(id=curve.id)
        self.assertTrue(cu2.params['coucou12']==45.)
        
        search = CurveDB.objects.filter_param('coucou12', value__gte=44)
        self.assertTrue(cu2 in search)
        
    def test_remove_param(self):
        curve = CurveDB()
        curve.set_data(pandas.Series([1,4,6]))
        curve.save()
        
        for i in range(20):
            curve.params['coucou' + str(i)] = i
        curve.save()
        curve = CurveDB.objects.get(id=curve.id)
        curve.params.pop("coucou12")
        curve.save()
        curve = CurveDB.objects.get(id=curve.id)
        self.assertTrue("coucou12" not in curve.params)
        
    def test_clear_columns(self):
        curve = CurveDB()
        curve.set_data(pandas.Series([1,4,6]))
        curve.save()
        
        curve.params['dummy_name'] = 89
        curve.save()
        curve = CurveDB.objects.get(id=curve.id)
        self.assertTrue("dummy_name" in [o.name for o in ParamColumn.objects.all()])
        
        curve.params.pop('dummy_name')
        curve.save()
        self.assertTrue("dummy_name" in [o.name for o in ParamColumn.objects.all()])
        clear_unused_columns()
        self.assertFalse("dummy_name" in [o.name for o in ParamColumn.objects.all()])

class Profiling(TestCase):
    def test_insert(self):
        curve = CurveDB()
        curve.set_data(pandas.Series([1,4,6]))
        curve.save()
        
        tic = time.time()
        for i in range(10):
            curve.params['coucou'] = i
            curve.save()
        print "time for saving 100 dummy curves: " , time.time() - tic
        
    def test_insert(self):
        curve = CurveDB()
        curve.set_data(pandas.Series([1,4,6]))
        curve.save()
        
        tic = time.time()
        for i in range(10):
            for j in range(10):
                curve.params['coucou' + str(j)] = j
                curve.save()
        print time.time() - tic