from pymadx import Tfs as _Tfs
from bisect import bisect as _bisect
import numpy as _np


class Aperture(_Tfs):
    def __init__(self, *args, **kwargs):
        _Tfs.__init__(self, *args, **kwargs)
        if 'debug' in kwargs:
            self.debug = kwargs['debug']
        else:
            self.debug = False
        # the tolerance below which, the aperture is considered 0
        self._tolerance = 1e-10
        self._UpdateCache()
        
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
                #self._aper1 = self.GetColumn('APER_1')
            #self._aper2 = self.GetColumn('APER_2')
            #self._aper3 = self.GetColumn('APER_3')
            #self._aper4 = self.GetColumn('APER_4')  
        except ValueError:
            pass

    def GetNonZeroItems(self):
        # prepare list of relevant aperture keys to check
        aperkeys = []
        aperkeystocheck = ['APER_%s' %n for n in [1,2,3,4]]
        for key in aperkeystocheck:
            if key in self.columns:
                aperkeys.append(key)
        if len(aperkeys) == 0:
            raise KeyError("This file does not contain APER_1,2,3 or 4 - required!")

        # prepare resultant tfs instance
        a = Aperture()
        a._CopyMetaData(self)
        for item in self:
            apervalues = _np.array([item[key] for key in aperkeys])
            nonzeros = apervalues > self._tolerance
            nonzero  = nonzeros.any() #if any are true
            if nonzero:
                key = self.sequence[self._iterindex]
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
        return self[self._GetIndexInCacheOfS(sposition)]
        
    def GetApertureForElementNamed(self, name):
        return self.GetRow(name)

    def ShouldSplit(self, rowDictionary):
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
        bdA1 = _np.diff(self._aper1[indexStart:indexEnd]) != 0
        bdA2 = _np.diff(self._aper2[indexStart:indexEnd]) != 0
        bdA3 = _np.diff(self._aper3[indexStart:indexEnd]) != 0
        bdA4 = _np.diff(self._aper4[indexStart:indexEnd]) != 0
        
        # find if there are any changes in aperture for any parameter
        shouldSplit = _np.array([bdA1, bdA2, bdA3, bdA4]).any()    

        if not shouldSplit:
            return False, [], []
        else:
            if self.debug:
                print 'Recommend splitting element'
            # should split!
            # work out s locations at split points
            
            # put all selection boolean arrays into one large 2D array
            # of nonzero differential vs aperture parameter
            bdA = _np.array([bdA1, bdA2, bdA3, bdA4])
            # get the a unique set of the indices where any aperture changes
            indices = _np.array(list(set(bdA.nonzero()[1])))
            indices += indexStart # add on offset to get index for whole data
            print indices
            sSplits = _np.array([self._ssorted[x] for x in indices])
            sSplitStart = _np.array(sSplits) #copy the starts
            sSplitStart = _np.insert(sSplitStart, 0, sStart)
            # work out the length of each section
            lSplits = sSplits - sStart
            print lSplits
            lSplits = _np.insert(lSplits, 0, 0)
            lSplits = _np.append(lSplits, l) # make length last one
            print lSplits
            lSplits = _np.diff(lSplits)

            # paranoid checks - trim / adjust last element to conserve length accurately
            if lSplits.sum() != l:
                lSplits[-1] = lSplits[-1] + (l - lSplits.sum())

            sSplitMid = sSplitStart + lSplits*0.5
            apertures = [self.GetApertureAtS(s) for s in sSplitMid]
            
            return True, lSplits, apertures


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
