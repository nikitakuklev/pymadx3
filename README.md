#pymadx#

A python package containing both utilities for processing and analysing MADX output.

## Authors ##

L. Nevay
S. Boogert
S. Walker
A. Abramov
W. Shields
J. Snuverink

## Setup ##

From within the pymadx root directory:

$ make install

or for development where the local copy of the repository is used
and can be reloaded with local changes:

$ make develop


```
$> python
>>> import pymadx
>>> t = pymadx.Data.Tfs("twiss.tfs")
```

## Dependencies ##

 * matplotlib
 * numpy
 * pytransport (optional)