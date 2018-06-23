# pymadx._General - general python scripts / tools
# Version 1.0
# L. Nevay, S.T.Boogert
# laurie.nevay@rhul.ac.uk

"""
General utilities for day to day housekeeping
"""

import os

def CheckFileExists(filename):
    i = 1
    parts = filename.split('.')
    basefilename = parts[0]
    if len(parts) > 1:
        extension = '.' + parts[1]
    else:
        extension = ''
    while os.path.exists(filename) :
        filename = basefilename+str(i)+extension
        i = i + 1
    return filename

def Chunks(l, n):
    """ Yield successive n-sized chunks from l.    """
    return [l[i:i+n] for i in range(0,len(l),n)]

def NearestEvenInteger(number):
    number = int(number)
    return number + number%2

def Cast(string):
    """
    Cast(string)
    
    tries to cast to a (python)float and if it doesn't work, 
    returns a string

    """
    try:
        return float(string)
    except (ValueError, TypeError):
        return string

def IsFloat(stringtotest):
    try:
        float(stringtotest)
        return True
    except (ValueError, TypeError):
        return False

def IndexOfElement(tfsinstance,markername):
    t = tfsinstance
    names = list(t.data['NAME'])
    try:
        i = names.index(markername)
    except ValueError:
        i = 0
        print 'Unknown element name'
    return i

def GetSixTrackAperType(aper1, aper2, aper3, aper4):
    """Return the Aperture type given the four aperture paramters.
    This is required because SixTrack aperture description files do
    not explictily state the aperture type.  It is instead encoded in
    the aperture parameters."""
    # I got this information from
    # http://lhc-collimation-project.web.cern.ch/lhc-collimation-project/BeamLossPattern/Code/BeamLossPattern_2005-06-17.tgz
    # on the page http://lhc-collimation-project.web.cern.ch/lhc-collimation-project/BeamLossPattern.htm#Source
    # By extracting the above tarball and inspecting Aperture.cpp, the
    # logic implemented below is found.
    if aper1 == 0 and aper2 == 0 and aper3 == 0 and aper4== 0:
        return ''
    elif aper1 == aper3 and aper2 == aper4: # Line 221 of Aperture.cpp
        return 'ELLIPSE'
    elif aper1 == aper3 and aper2 < aper4: #
        return 'LHCSCREEN'
    elif aper1 < aper3 and aper2 == aper4:
        return 'LHCSCREEN'
    elif aper1 == 0 and aper2 == 0:
        return 'RACETRACK' # Line 252 of Aperture.cpp
    elif aper3 == 0:
        return 'RECTANGLE'
    msg = ("Sixtrack aperture not recognised:"
           " (A1, A2, A3, A4) = ({}, {}, {}, {})".format(aper1, aper2,
                                                         aper3, aper4))
    raise ValueError(msg)
