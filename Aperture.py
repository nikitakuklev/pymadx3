"""
Class to load apertures in Tfs files and methods to manipulate them.
Some methods are part of the class and others are unbound.
"""

from pymadx import Tfs as _Tfs
from bisect import bisect as _bisect
import numpy as _np

_madxAperTypes = { 'CIRCLE',
                   'RECTANGLE',
                   'ELLIPSE',
                   'RECTCIRCLE',
                   'LHCSCREEN',
                   'MARGUERITE',
                   'RECTELLIPSE',
                   'RACETRACK',
                   'OCTAGON'}

class Aperture(_Tfs):
    """
    A class based on (which inherits) the Tfs class for reading aperture information.
    This allows madx aperture information in Tfs format to be loaded, filtered and 
    queried. This also provides the ability to suggest whether an element should be
    split and therefore what the aperture should be.

    This class maintains a cache of aperture information as a function of S position.

    'quiet' being defined in kwargs will silence a warning about unknown aperture types.

    """
    def __init__(self, *args, **kwargs):
        _Tfs.__init__(self, *args, **kwargs)
        self.debug = False
        if 'debug' in kwargs:
            self.debug = kwargs['debug']
            
        # the tolerance below which, the aperture is considered 0
        self._tolerance = 1e-6
        self._UpdateCache()
        if 'quiet' not in kwargs:
            self.CheckKnownApertureTypes()
        
    def _UpdateCache(self):
        # create a cache of which aperture is at which s position
        # do this by creatig a map of the s position of each entry
        # with the associated 
        self.cache = {}

        print('Aperture> preparing cache')
        for item in self:
            s = item['S']
            if s in self.cache.keys():
                #if existing one is zero and other isn't replace it
                if ZeroAperture(self.cache[s]) and NonZeroAperture(item):
                    self.cache[s] = item
            else:
                self.cache[s] = item

        # dictionary is not ordered to keep list of ordered s positions
        self._ssorted = self.cache.keys()
        self._ssorted.sort()

        # pull out some aperture values for conevience
        # try this as class may be constructed with no data
        try:
            for key in ['APER_1', 'APER_2', 'APER_3', 'APER_4']:
                setattr(self, '_'+str.lower(key), self.GetColumn(key))
        except ValueError:
            pass

    def CheckKnownApertureTypes(self):
        failed = False
        ts = set(self.GetColumn('APERTYPE'))
        for t in ts:
            if t not in _madxAperTypes:
                failed = True
                print 'Warning: Aperture type ',t,'is not a valid MADX aperture types.'

        if failed:
            PrintMADXApertureTypes()

    def SetZeroTolerance(self, tolerance):
        """
        Set the value below which aperture values are considered 0.
        """
        self._tolerance = tolerance

    def GetNonZeroItems(self):
        """
        Return a copy of this class with all non-zero items removed.

        """
        print 'Aperture> removing zero aperture items'
        # prepare list of relevant aperture keys to check
        aperkeys = []
        aperkeystocheck = ['APER_%s' %n for n in [1,2,3,4]]
        for key in aperkeystocheck:
            if key in self.columns:
                aperkeys.append(key)
            else:
                print key,' will be ignored as not in this aperture Tfs file'
        if len(aperkeys) == 0:
            raise KeyError("This file does not contain APER_1,2,3 or 4 - required!")

        # prepare resultant tfs instance
        a = Aperture(debug=self.debug)
        a._CopyMetaData(self)
        for item in self:
            apervalues = _np.array([item[key] for key in aperkeys])
            nonzeros = apervalues > self._tolerance
            nonzero  = nonzeros.any() #if any are true
            if nonzero:
                if item['APER_1'] < self._tolerance:
                    continue # aper1 must at least be non zero
                key = self.sequence[self._iterindex]
                a._AppendDataEntry(key, self.data[key])
        a._UpdateCache()
        return a

    def GetEntriesBelow(self, value=8, keys='all'):
        return self.RemoveAboveValue(value,keys)
    
    def RemoveAboveValue(self, limits=8, keys='all'):
        print 'Aperture> removing any aperture entries above',limits
        if keys == 'all':
            aperkeystocheck = ['APER_%s' %n for n in [1,2,3,4]]
        elif type(keys) in (float, int):
            aperkeystocheck = [keys]
        elif type(keys) in (list, tuple):
            aperkeystocheck = list(keys)

        limitvals = _np.array(limits) # works for single value, list or tuple in comparison

        # check validity of the supplied keys
        aperkeys = []
        for key in aperkeystocheck:
            if key in self.columns:
                aperkeys.append(key)
            else:
                print key,' will be ignored as not in this aperture Tfs file'

        a = Aperture(debug=self.debug)
        a._CopyMetaData(self)
        for item in self:
            apervals = _np.array([item[key] for key in aperkeys])
            abovelimit = apervals > limitvals
            abovelimittotal = abovelimit.any() # if any are true
            if not abovelimittotal:
                key = self.sequence[self._iterindex]
                a._AppendDataEntry(key, self.data[key])
        a._UpdateCache()
        return a

    def GetUniqueSPositions(self):
        return self.RemoveDuplicateSPositions()

    def RemoveDuplicateSPositions(self):
        """
        Takes the first aperture value for entries with degenerate S positions and
        removes the others.
        """
        print 'Aperture> removing entries with duplicate S positions'
        # check if required at all
        if len(self) == len(self._ssorted):
            # no duplicates!
            return self
        
        a = Aperture(debug=self.debug)
        a._CopyMetaData(self)
        u,indices = _np.unique(self.GetColumn('S'), return_index=True)
        for ind in indices:
            key = self.sequence[ind]
            a._AppendDataEntry(key, self.data[key])
        a._UpdateCache()
        return a

    def _GetIndexInCacheOfS(self, sposition):
        index = _bisect(self._ssorted, sposition)
        if index > 0:
            return index - 1
        else:
            return index

    def GetApertureAtS(self, sposition):
        """
        Return a dictionary of the aperture information specified at the closest
        S position to that requested - may be before or after that point.
        """
        return self[self._GetIndexInCacheOfS(sposition)]

    def GetExtentAtS(self, sposition):
        """
        Get the x and y maximum +ve extent (assumed symmetric) for a given
        s position.  Calls GetApertureAtS and then GetApertureExtent.
        """
        element = GetApertureAtS(sposition)
        x,y     = GetApertureExtent(element)
        return x,y
        
    def GetApertureForElementNamed(self, name):
        """
        Return a dictionary of the aperture information by the name of the element.
        """
        return self.GetRow(name)

    def GetExtent(self, name):
        """
        Get the x and y maximum +ve extent (assumed symmetric) for a given
        entry by name.  Calls GetApertureForElementNamed and then GetApertureExtent.
        """
        element = self.GetApertureForElementNamed(name)
        x,y     = GetApertureExtent(element)
        return x,y

    def GetExtentAll(self):
        """
        Get the x and y maximum +ve extent (assumed symmetric) for the full
        aperture instance.

        returns x,y where x and y are 1D numpy arrays
        """
        x,y = GetApertureExtents(self)

        return x,y

    def ReplaceType(self, existingType, replacementType):
        print 'Aperture> replacing',existingType,'with',replacementType
        et = existingType    #shortcut
        rt = replacementType #shortcut
        try:
            index = self.columns.index('APERTYPE')
        except ValueError:
            print 'No apertype column, therefore no type to replace'
            return
        for item in self:
            try:
                if item['APERTYPE'] == et:
                    self.data[item['NAME']][index] = rt
            except KeyError:
                return

    def ShouldSplit(self, rowDictionary):
        """
        Suggest whether a given element should be split as the aperture information
        in this class suggests multiple aperture changes within the element.

        Returns bool, [], []
        
        which are in order:

        bool - whether to split or not
        []   - list of lengths of each suggested split
        []   - list of the aperture dictionaries for each one

        """
        l      = rowDictionary['L']
        sEnd   = rowDictionary['S']
        sStart = sEnd -l
        
        indexStart = self._GetIndexInCacheOfS(sStart)
        indexEnd   = self._GetIndexInCacheOfS(sEnd)
        # get the s positions of any defined aperture points within
        # the length of the element
        apertureSValuesInRange = self._ssorted[indexStart:indexEnd]

        # calculate differentials of aperture values in range of the element
        # test if any are non-zero
        bdA1 = _np.diff(self._aper_1[indexStart:indexEnd]) != 0
        bdA2 = _np.diff(self._aper_2[indexStart:indexEnd]) != 0
        bdA3 = _np.diff(self._aper_3[indexStart:indexEnd]) != 0
        bdA4 = _np.diff(self._aper_4[indexStart:indexEnd]) != 0
        
        # find if there are any changes in aperture for any parameter
        shouldSplit = _np.array([bdA1, bdA2, bdA3, bdA4]).any()

        if self.debug:
            print 'length: ',l,', S (start): ',sStart,', S (end): ',sEnd
            print 'Index (start): ',indexStart,', Index(end): ',indexEnd
            print 'Any difference in aper1: ',bdA1
            print 'Any difference in aper2: ',bdA2
            print 'Any difference in aper3: ',bdA3
            print 'Any difference in aper4: ',bdA4

        if not shouldSplit:
            # return false and the aperture model to be use for the whole item
            sMid = (sEnd - sStart) / 2
            return False, [l], [self.GetApertureAtS(sMid)]
        else:
            if self.debug:
                print 'Recommend splitting element'
            # should split!
            # work out s locations at split points
            
            # put all selection boolean arrays into one large 2D array
            # of nonzero differential vs aperture parameter
            bdA = _np.array([bdA1, bdA2, bdA3, bdA4])
            # get the a unique set of the indices where any aperture changes
            # nonzero->bool array, take only which items (rows) have nonzero diffs, take set of to remove duplication
            indices = _np.array(list(set(bdA.nonzero()[1]))) 
            indices += indexStart # add on offset to get index for whole data
            if self.debug:
                print indices
            sSplits = _np.array([self._ssorted[x] for x in indices]) # s positions of aperture changes
            if len(sSplits) > 1:
                while sSplits[0] < sStart:
                    sSplits = sSplits[1:] # remove any elements before the start position of this element
            sSplitStart = _np.array(sSplits) #copy the starts
            sSplitStart = _np.insert(sSplitStart, 0, sStart) # prepend s of first element
            # work out the length of each section
            lSplits = sSplits - sStart

            # replace any <0 lengths ie nearest aperture definition behind start of this object
            # ignore these and only take aperture definitions in front of the element
            lSplits     = lSplits[lSplits > 0]
            
            if self.debug:
                print 'Aperture> length of splits: ',lSplits

            # lSplits is just the length of the proposed split points from the start
            # make them a local S within the element by prepending 0 and appending L(ength)
            lSplits = _np.insert(lSplits, 0, 0)
            lSplits = _np.append(lSplits, l) # make length last one
            
            lSplits = _np.diff(lSplits)

            if self.debug:
                print 'Aperture> length of splits after checks: ',lSplits

            # paranoid checks - trim / adjust last element to conserve length accurately
            if lSplits.sum() != l:
                lSplits[-1] = lSplits[-1] + (l - lSplits.sum())

            # get the mid point of each split segment for asking what the aperture should be
            sSplitMid = sStart + lSplits*0.5
            apertures = [self.GetApertureAtS(s) for s in sSplitMid]

            # check result of attempted splitting
            result = True if len(sSplits)>1 else False
            if len(apertures) > len(sSplits):
                apertures = apertures[:len(sSplits)] #should index 1 ahead - counteracts 0 counting
            
            return result, lSplits, apertures

def CheckItsTfsAperture(tfsfile):
    """
    Ensure the provided file is an Aperture instance.  If it's a string, ie path to
    a tfs file, open it and return the Tfs instance.
    
    tfsfile can be either a tfs instance or a string.
    """
    if type(tfsfile) == str:
        aper = Aperture(tfsfile)
    elif type(tfsfile) == pymadx.Aperture.Aperture:
        aper = tfsfile
    else:
        raise IOError("Not pymadx.Aperture.Aperture file type: "+str(tfsfile))
    return aper

def PrintMADXApertureTypes():
    print 'Valid MADX aperture types are:'
    for t in _madxAperTypes:
        print t
        
def GetApertureExtents(aperture):
    """
    Loop over a pymadx.Aperture.Aperture instance and calculate the maximum
    +ve extent (assumed symmetric) in x and y.

    returns x,y where x and y and 1D numpy arrays
    """
    aper1 = aperture.GetColumn('APER_1')
    aper2 = aperture.GetColumn('APER_2')
    aper3 = aperture.GetColumn('APER_3')
    aper4 = aperture.GetColumn('APER_4')
    apertureType = aperture.GetColumn('APERTYPE')

    x = []
    y = []
    for i in range(len(aperture)):
        xt,yt = GetApertureExtent(aper1[i], aper2[i], aper3[i], aper4[i], apertureType[i])
        x.append(xt)
        y.append(yt)

    x = _np.array(x)
    y = _np.array(y)
    return x,y

def GetApertureExtent(aper1, aper2, aper3, aper4, aper_type):
    """
    Get the maximum +ve half extent in x and y for a given aperture model and (up to)
    four aperture parameters.

    returns x,y
    """
    
    if  aper_type not in _madxAperTypes:
        raise ValueError('Unknown aperture type: ' + aper_type)

    x = aper1
    y = aper2

    if aper_type == 'CIRCLE':
        x = aper1
        y = aper1
    if aper_type in ['RECTANGLE', 'ELLIPSE', 'OCTAGON']:
        x = aper1
        y = aper2
    elif aper_type in ['LHCSCREEN', 'RECTCIRCLE', 'MARGUERITE']:
        x = min(aper1, aper3)
        y = min(aper2, aper3)
    if aper_type == 'RECTELLIPSE':
        x = min(aper1, aper3)
        y = min(aper2, aper4)
    elif aper_type == 'RACETRACK':
        x = aper3 + aper1
        y = aper2 + aper3
    
    return x,y


def NonZeroAperture(item):
    tolerance = 1e-9
    test1 = item['APER_1'] > tolerance
    test2 = item['APER_2'] > tolerance
    test3 = item['APER_3'] > tolerance
    test4 = item['APER_4'] > tolerance

    return test1 or test2 or test3 or test4

def ZeroAperture(item):
    tolerance = 1e-9
    test1 = item['APER_1'] < tolerance
    test2 = item['APER_2'] < tolerance
    test3 = item['APER_3'] < tolerance
    test4 = item['APER_4'] < tolerance

    return test1 and test2 and test3 and test4
