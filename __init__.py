"""
pymadx - Madx TFS file parser

Authors: L. Nevay, S. Boogert
2014 11 14

Tfs           - a loader class
Visualisation - visualisation of the loaded lattice

"""

import Convert

from Tfs import Tfs
from Aperture import Aperture
from TfsArray import TfsArray
import Builder
import Ptc
from PtcAnalysis import PtcAnalysis 
from Beam import Beam
from MadxTfs2Ptc import MadxTfs2Ptc

# things the depend on matplotlib (optional)
try:
    import Plot
    from PtcPlot import PtcPlot
except ImportError:
    pass

from _General import CheckItsTfs

__all__ = ['Tfs','TfsArray','Beam','Builder','Plot','Ptc','MadxTfs2Ptc','PtcPlot','PtcAnalysis']
