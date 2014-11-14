"""
Conversion from and to various formats related to the MadX format

See individual methods for documentation

"""

import _Mad8

#wrapper for clean interface
#wrapper functions should be placed in here and long complicated 

def Mad8ToMadX(inputfilename):
    """
    Convert a Mad8 file to the syntax of a MadX file.

    The output file name will be the input file name with
    the file extension replaced by .xsifx
    """
    _Mad8.Mad8ToMadX(inputfilename)
