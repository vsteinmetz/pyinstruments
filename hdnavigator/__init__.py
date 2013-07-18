"""This module helps you navigating in a defaultPath, for instance on the data folder of a server.
Navigation with this module also implies that the normal path in the os module is modified as in os.chdir() or cd .. 
Be carreful though, the reciprocal is wrong : os.chdir("somewhere") won't change anything to the state of this module.

To change the default path, simply rename the property conf.defaultPath (e.g.: HDnavigator.conf.defaultPath = "Z:/measurements")

==========
functions:
==========
next("someName")                  :generates a filename with a nice incremented numbering

next_dir("some_name")             :creates a new directory at the same depth as the current one, except if the current one is a date_directory or the defaultPath directory

subdir("some_name",prefix = True) :creates a new directory inside the current one, with/without nice numbering. One advantage of using the numbering is that if the current position gets lost (change back and forth of conf.defaultPath for instance), the module finds its way back automatically through the part of the directories that are numbered

new_day("some_name")              :creates a directory starting with today's date directly under defaultPath, complains if it already exists

up()                              :goes up by one directory
"""

from navigatorgui import nav
