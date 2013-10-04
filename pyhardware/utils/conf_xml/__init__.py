"""
======================================================================
===    conf_xml
======================================================================
This module allows to store configuration data easily in a xml file.
Typical use is
from conf_xml import conf,default_file
c = conf(default_file(__file__))

##writing value
c.sub("obj1",prop1 = "valeur1", prop2 = "valeur2")
c.serialize()

##reading value
c.obj1.prop1
c.obj1["prop1"]
"""

from conf import conf, default_file