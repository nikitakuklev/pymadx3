===============
Version History
===============

v 1.6 - 2018 / ?? / ??
======================

General
-------

* Reimplemented machine diagram drawing to be more efficient when zooming and
  fix zordering so bends and then quadrupoles are always on top.


v 1.5 - 2018 / 08 / 24
======================

New Features
------------

* Support for tkicker.
* Support for kickers in MADX to PTC.

General
-------

* Improved aperture handling.

Bug Fixes
---------

* Several bugs in Aperture class fixed.


v 1.4 - 2018 / 06 / 23
======================

New Features
------------

* Support of just gzipped files as well as tar gzipped.

General
-------

* Improved SixTrack aperture handling.

v 1.2 - 2018 / 05 / 23
======================

New Features
------------

* Write a beam class instance to a separate file.
* Add ptc_track maximum aperture to a model.
* Concatenate TFS instances.
* N1 aperture plot as well as physical aperture plot.
* Output file naming for plots for MADX MADX comparison.
* MADX Transport comparison plots.

General
-------

* Changes to some plot arguments.
* 'Plot' removed from plot functions name as redundant.
* Transport conversion moved to pytransport.
  
Bug Fixes
---------

* Machine plot now deals with 'COLLIMATOR' type correctly.


v 1.1 - 2018 / 04 / 10
======================

New Features
------------

* Improved options for writing PTC job for accurate comparison.
* Support for subrelativistic machines - correct MADX definition of dispersion.
* Plots for beam size including dispersion.
* MADX MADX Twiss comparison plots.

Bug Fixes
---------

* Removal of reverse slicing as it didn't work and is very difficult to support
  as MADX typically returns optical functions at the end of an element. Some
  columns however are element specific (such as L).
* Fixed exception catching.
* Fix beam size for subrelativistic machines. MADX really provides Dx/Beta.
* Fix index searching from S location.
* Fix PTC analysis.
* Fix conversion to PTC for fringe fields.

v 1.0 - 2017 / 12 / 05
======================

New Features
------------

* GPL3 licence introduced.
* Compatability with PIP install system.
* Manual.
* Testing suite.
