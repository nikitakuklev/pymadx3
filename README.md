#pyMadx#

A python package containing both utilities for processing and analysing MADX output

## Authors ##

L. Nevay
S. Boogert

## Setup ##
The module currently requires no setup and can be used by adding the pymadx directory to your python path.

git clone http://bitbucket.org/stewartboogert/pybdsim .

-> edit your terminal (perhaps bash) profile


```
#!csh

$PYTHONPATH=$PYTHONPATH:/path/to/where/you/put/pymadx

```


```
#!python

$>python
$>>> import pymadx
$>>> t = pymadx.Tfs("twiss")
```

# Dependencies #
