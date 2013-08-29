
=============================================
pyinstruments: data acquisition toolkit
=============================================

*program less and do more science... better*


What is it
==========

**pyinstruments** is a Python package to control/get data from measurement and
automation devices. Control of the remote instruments can be done via one of 
the following protocols:
  
  - ivi drivers (using the lower level package pyivi)
  - visa
  - serial

Using IVI-drivers greatly simplifies your life because :

  1/. The lower level layer is fully transparent for the user (pyivi provides a common interface for each instrument type).
  
  2/. **zero** extra work is needed to interface an instrument for which an IVI driver is provided.

pyinstruments is composed of two **independant** packages (can be run on 2 remote computers!).

  - **pyhardwaredb** for the hardware communication (This package itself is a thin wrapper around pyhardware). Because it heavily relies on ivi-drivers and com-interoperability, this package is intended to run on a windows machine.
  - **curvefinder** to display in quasi real-time the curves acquired (This module could be run on any platform).

The strict separation between plotting and data-acquistion processes ensures that scripted data-acquisitions won't be affected by user interactions or plotting dead-times.


Main Features
=============

The curves are stored in a (django-abstracted) database with all necessary metadata 
(bandwidth, averaging...) together with a list of user-defined tags and comments. 
The curvefinder module allows monitoring new incoming curves, as well as querying
the database for old curve by date, tags...

The hardware module has a Graphical User Interface to quickly get a curve from an instrument and configure the way instruments are interfaced.

Dependencies
============

Direct dependancies for pyinstruments are:
  - django > 1.5
  - PyQt4
  - guidata
  - guiqwt
  - pyhardware <-- pyivi <-- (ctypes + comtypes)


Installation
============


The windows installer takes care of all the dependancies that are not standards in version 2.7.3.1 of pythonxy.

The other option to install pyinstruments is to use pip from a command shell (also available in pythonxy)::

		pip install pyinstruments

pyinstruments and its three 'exotic' dependencies can also be uninstalled using pip::

		pip uninstall pyinstruments
		pip uninstall pyhardware
		pip uninstall pyivi



Try it out!
===========

The installation is single click (since v 0.1.15), desktop icons are created 
to launch both graphical user interfaces.

The project is hosted on GitHub, and still in a starting phase, contributions and feedback
are warmly welcome!

<https://github.com/SamuelDeleglise/pyinstruments>