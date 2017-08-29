============
Installation
============


Requirements
------------

 * pymadx was developed for the Python 2.7 series.

pymadx depends on the following Python packages not included with Python:

 * matplotlib
 * numpy

Installation
------------


A `setup.py` file required for a correct python installation is currently under development.

Currently, we recommend the user clones the source repository and exports the parent directory
to their PYTHONPATH environmental variable. This will allow Python to find pymadx.::

  pwd
  /Users/nevay/physics/reps
  git clone http://bitbucket.org/jairhul/pymadx
  ls
  > pymadx
  export PYTHONPATH=/Users/nevay/physics/reps

  python
  >>> import pymadx # no errors!
