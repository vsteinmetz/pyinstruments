=============================================
pyhardware: data acquisition hub
=============================================

**pyhardware** combines in one package several data-acquisition protocols:
  - ivi drivers (using the lower level package pyivi)
  - visa
  - serial

Each instrument connected to the machine can be autodetected, and assigned a unique logical name.
Graphical tools are provided to configure the different instruments and the way they should 
be interfaced.

It uses the lower-level package pyivi to communicate with ivi-drivers on the machine. The specificity of this package
is to directly interact with the ivi-framework using comtypes and ctypes. This makes fully use of the interchangeability feature of IVI instruments:
new instruments can be installed in a single click by simply installing the IVI-drivers provided by the manufacturer.

pyhardware is part of a higher-level package : pyinstruments, that you might want to check out : it adds-up database-capabilities to store the curves from the instruments in a consistent way.

Dependencies
============
  - PyQt4
