===============
Version History
===============

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
