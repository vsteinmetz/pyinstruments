"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from pyinstruments.curvestore.models import CurveDB

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
        
   
class TestTagsGui(TestCase):
    def test_child(self):
        tag, cr = Tag.objects.get_or_create(name='tag')
        tag, cr = Tag.objects.get_or_create(name='tag1')
        tag2, cr = Tag.objects.get_or_create(name='tag1/tag2')    
        tag3, cr = Tag.objects.get_or_create(name='tag1/tag3')
        ROOT.build_children_from_model()
        from pyinstruments.curvestore.tag_widget import TagTreeView
        from guidata import qapplication
        app = qapplication()
        t = TagTreeView()
        t.show()
        app.exec_()
        
        ROOT.build_children_from_model()
        app = qapplication()
        t = TagTreeView()
        t.show()
        app.exec_()
