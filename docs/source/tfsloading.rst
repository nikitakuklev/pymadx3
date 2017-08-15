===============================
TFS File Loading & Manipulation
===============================

MADX outputs Twiss information as well as PTC tracking data in their own Table
File System (TFS). This is the only format used by MADX. pymadx includes a class
called Tfs for the purpose of loading and manipulating this data.

The TFS format is described in the MADX manual available from madx.cern.ch. The format
roughly is described as a text file. The file contains first a header with key and
value pairs for one-off definitions. This is proceeded by a line
with column names and a line with the data type of each column. After this each line
typically represents the values of the lattice for a particular element with each new
line containing the values at a subsequent element in the lattice. We maintain the
concept of this table and refer to 'rows' and 'columns'.

Tfs Class Features
------------------

* Loading of TFS files.
* Loading of TFS files compressed and archived with .tar.gz suffix without decompressing.
* Report a count of all different element types.
* Get a particular column.
* Get a particular row.
* Get elements of a particular type.
* Get a numerical index from the name of the element.
* Find the curvilinear S coordinate of an element by name.
* Find the name of the nearest element at a given S coordinate.
* Plot an optics diagram.
* Roll a lattice to start from a different point.
* Calculate a beam size given the Twiss parameters, dispersion and emittance (in the header).
* Determining whether a given component perturbs the beam.
* Extract a 'segment' if PTC data is present.
* Slice a lattice (in the Python sense) with new S coordinates.


Loading
-------

A file may be loading by constructing a Tfs instance from a file name.

>>> import pymadx
>>> a = pymadx.Tfs("myTwissFile.tfs")

.. note:: The import will be assumed from now on in examples.

A file compressed using tar and gzip may also be loaded without first uncompressing
without any difference in functionality. Not temporary files are created::

  tar -czf myTwissFile.tar.gz myTwissFile.fs
  
>>> import pymadx
>>> a = pymadx.Tfs("myTwissFile.tar.gz")

.. note:: The detection of a compressed file is based on 'tar' or 'gz' existing
	  in the file name.

Twiss File Preparation
----------------------

You may export twiss data from MADX with a choice of columns. We often find it beneficial
to not specify any columns at all, which results in all available columns being written.
This large number (~70) makes the file less human-readable but ensures no information is
omitted. Such an export will also increase the file size, however, we recommend compressing
the file with tar and gzip as the ASCII files compress very well with a typically compression
ratio of over 10:1.

The following MADX syntax in a MADX input script will prepare a Tfs file with all columns where
"SEQUENCENAME" is the name of the sequence in MADX.::

  select,flag=twiss, clear; 
  twiss,sequence=SEQUENCENAME, file=outputfilename.tfs;

Plotting
--------

A simple optics plot may be made
