from django.test import TestCase
from pyinstruments.curvestore.models import Tag, top_level_tag

class TestTagModel(TestCase):
    def test_top_level_tag(self):
        """
        
        """
        self.tag = Tag(name='tag1')
        self.tag.save()
        self.tag2 = Tag(name='tag2')
        self.tag2.save()

        self.assertTrue(top_level_tag()[1].name == 'tag2')

