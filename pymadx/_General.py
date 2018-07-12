# pymadx._General - general python scripts / tools
# Version 1.0
# L. Nevay, S.T.Boogert
# laurie.nevay@rhul.ac.uk

"""
General utilities for day to day housekeeping
"""

import os
import math

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

def GetSixTrackAperType(a1, a2, a3, a4):
    """Return the Aperture type given the four aperture paramters.
    This is required because SixTrack aperture description files do
    not explictily state the aperture type.  It is instead encoded in
    the aperture parameters.  In general these will be RECTELLIPSEs"""

    # Rectellipse is the intersection of an ellipse with a concentric rectangle.
    # a1 = rectangle half-width (i.e. x)
    # a2 = rectangle half-height (i.e. y)
    # a3 = ellipse x semi-axis  (i.e. x)
    # a4 = ellipse y semi-axis  (i.e. y)

    # In general all the apertures are rectellipses except for two
    # cases:

    # a3=0 denotes a rectangle (since a3 = 0 = empty set and thus has
    # no meaning for a rectellipse).

    # a1 == 0 and a2 == 0 apparently denotes a RACETRACK, but I'm not
    # sure BeamLossPattern supports this (even though there is the source
    # for it).

    # Rectellipse with the parameters which result in an ellipse
    if a1 == a3 and a2 == a4:
        return "RECTELLIPSE"
    # rectellipse with horizontal edges on top (parallel to x-axis)
    elif a1 == a3 and a2 < a4:
        return "RECTELLIPSE"
    # rectellipse with horizontal edges on top (parallel to y-axis)
    elif a1 < a3 and a2 == a4:
        return "RECTELLIPSE"
    elif a1 == 0 and a2 == 0:
        raise ValueError("Racetrack!  Not supported by BeamLossPattern!")
    elif a3 == 0:
        raise ValueError("Rectangle!  Not supported here yet!")

    msg = ("Sixtrack aperture not recognised:"
           " (A1, A2, A3, A4) = ({}, {}, {}, {})".format(aper1, aper2,
                                                         aper3, aper4))
    raise ValueError(msg)
