
=============================================
pyinstruments: data acquisition toolkit
=============================================

*program less and do more science... better*


What is it
==========

**pyinstruments** is a Python package to control/get data from measurement and
automation devices. Control of the remote instruments can be done via one of 
the following protocols:
  
  - Visa
  - pythondotnet
  - comtypes
  - serial

The syntax of the higher level functions follows the IVI (Interchangeable Virtual Instruments)
guidelines. This allows:

  1/. a lower level layer fully transparent for the user.
  
  2/. **zero** extra work to interface an instrument for which an IVI driver is provided.

pyinstruments is composed of two **independant** packages (can be run on 2 remote computers!).

  - pyhardware for the hardware communication
  - curvefinder to display in quasi real-time the curves acquired.

In this way, in the case of scripted data-acquisition, the process is not affected 
at all by the plotting and user interactions.


Main Features
=============

The curves are stored in a (django-abstracted) database with all necessary metadata 
(bandwidth, averaging...) together with a list of user-defined tags and comments. 
The curvefinder module allows monitoring new incoming curves, as well as querying
the database for old curve by date, tags...

For simple tasks, the hardware module also has a simple Graphical User Interface
to quickly get a curve from an instrument...

Note: the hardware package can also be used independantly of the other modules.

Note2: in a near future, the modularity of the hardware package will increase,
in particular, external instrumentation drivers will be easily imported and
an independant package to interface IVI-instruments will be released.


Dependencies
============

  - pythondotnet: The hardware package requires windows OS to interface instruments via the dotnet protocol. The plotting one could run under any OS. Builds for windows can be found at http://www.lfd.uci.edu/~gohlke/pythonlibs/#pythonnet
  - Pandas http://pandas.pydata.org/ __ 0.10.1 or higher
  - PyQt4
  - guidata
  - guiqwt
  - django __ 1.5 or higher


Try it out!
===========

The installation is single click (since v 0.1.15), desktop icons are created 
to launch both graphical user interfaces.

The project is hosted on GitHub, and still in a starting phase, contributions
are warmly welcome!

<https://github.com/SamuelDeleglise/pyinstruments>