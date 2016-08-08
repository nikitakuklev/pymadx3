import tarfile
import numpy as _np
import copy as _copy
import string as _string
import re as _re

try:
    import Plot as _Plot
except ImportError:
    pass

from copy import deepcopy

#object inheritance is only for type comparison

class Tfs(object):
    """
    MADX Tfs file reader

    >>> a = Tfs()
    >>> a.Load('myfile.tfs')
    >>> a.Load('myfile.tar.gz') -> extracts from tar file

    or 

    >>> a = Tfs("myfile.tfs")

    | `a` has data members:
    | header      - dictionary of header items
    | columns     - list of column names
    | formats     - list of format strings for each column
    | data        - dictionary of entries in tfs file by name string
    | sequence    - list of names in the order they appear in the file
    | nitems      - number of items in sequence

    NOTE: if no column "NAME" is found, integer indices are used instead

    See the various methods inside a to get different bits of information:
    
    >>> a.ReportPopulations?

    Examples:

    >>> a.['IP.1'] #returns dict for element named "IP.1"
    >>> a[:30]     #returns list of dicts for elements up to number 30
    >>> a[345]     #returns dict for element number 345 in sequence
    
    """
    def __init__(self,filename=None,**kwargs):
        object.__init__(self) #this allows type comparison for this class
        self.index       = []
        self.header      = {}
        self.columns     = []
        self.formats     = []
        self.data        = {}
        self.sequence    = []
        self.nitems      = 0
        self.nsegments   = 0
        self.segments    = []
        self.filename    = filename
        if type(filename) == str:
            self.Load(filename)
        elif type(filename) == Tfs:
            self._DeepCopy(filename)
        
    def Clear(self):
        """
        Empties all data structures in this instance.
        """
        self.__init__()
    
    def Load(self,filename):
        """
        >>> a = Tfs()
        >>> a.Load('filename.tfs')
        
        Read the tfs file and prepare data structures. If 'tar' or 'gz are in 
        the filename, the file will be opened still compressed.
        """
        if ('tar' in filename) or ('gz' in filename):
            print 'pymadx.Tfs.Load> zipped file'
            tar = tarfile.open(filename,'r')
            f = tar.extractfile(tar.firstmember)
        else:
            print 'pymadx.Tfs.Load> normal file'
            f = open(filename)
        
        #first pass at file - need to check if it has 'NAME' column
        #if it has name, use that, otherwise use an integer
        #find column names line
        for line in f:
            sl = line.strip('\n').split()
            if line[0] == '*':
                #name
                self.columns.extend(sl[1:]) #miss "*" from column names line
                break
        if 'NAME' in self.columns:
            usename = True #use the name
        else:
            usename = False #no name column - use an index
        self.columns =  [] #reset columns for proper data read in
        f.seek(0) #reset file back to the beginning for reading in data

        #segment specific stuff
        segment_i = 0 #actual segment number in data may not be zero counting - use this variable
        segment_name = 'NA'
        #always include segments - put as first column in data
        self.columns.append("SEGMENT")
        self.formats.extend("%d")
        self.columns.append("SEGMENTNAME")
        self.formats.extend("%s")

        namecolumnindex = 0
        
        #read in data
        for line in f:
            splitline = line.strip('\n').split()
            sl        = splitline #shortcut
            if line[0] == '@':
                #header
                self.header[sl[1]] = Cast(sl[-1])
            elif line[0] == '*':
                #name
                self.columns.extend(sl[1:]) #miss *
                if "NAME" in self.columns:
                    namecolumnindex = self.columns.index("NAME")
            elif line[0] == '$':
                #format
                self.formats.extend(sl[1:]) #miss $
            elif '#' in line[0]:
                #segment line
                d = [Cast(item) for item in sl[1:]]
                segment_i    = d[0]
                segment_name = d[-1]
                self.nsegments += 1 # keep tally of number of segments
                self.segments.append(segment_name)
            else:
                #data
                d = [Cast(item) for item in sl]
                d.insert(0,segment_name) #prepend segment info
                d.insert(0,segment_i) #this one becomes the first item matching the column index
                if usename:
                    name = self._CheckName(d[namecolumnindex])
                else:
                    name = self.nitems
                self.sequence.append(name) # keep the name in sequence
                self.data[name] = d        # put in data dict by name
                self.nitems += 1           # keep tally of number of items
                
        f.close()
        
        #additional processing
        self.index = range(0,len(self.data),1)
        if 'S' in self.columns:
            self.smax = self[-1]['S']
            sindex = self.ColumnIndex('S')
            sEnd = self.GetColumn('S')  #calculating the mid points as the element
            sEnd = _np.insert(sEnd,0,0)
            sMid = (sEnd[:-1] + sEnd[1:])/2

            for i, name in enumerate(self.sequence):
                self.data[name].append(self.data[name][sindex]) # copy S to SORIGINAL
                self.data[name].append(sMid[i])
            self.columns.append('SORIGINAL')
            self.columns.append('SMID')
        else:
            self.smax = 0

        #Check to see if input Tfs is Sixtrack style (i.e no APERTYPE, and is instead implicit)
        if 'APER_1' in self.columns and 'APERTYPE' not in self.columns:
            self.columns.append('APERTYPE')

            for key, element in self.data.iteritems():
                aper1 = element[self.columns.index('APER_1')]
                aper2 = element[self.columns.index('APER_2')]
                aper3 = element[self.columns.index('APER_3')]
                aper4 = element[self.columns.index('APER_4')]
                apertype = self.GetSixTrackAperType(aper1,aper2,aper3,aper4)

                element.append(apertype)



        self._CalculateSigma()
        self.names = self.columns

    def _CalculateSigma(self):
        if 'GAMMA' not in self.header:
            self.header['BETA'] = 1.0 # assume super relativistic
        else:
            self.header['BETA'] = _np.sqrt(1.0 - (1.0/(self.header['GAMMA']**2)))

        # check this file has the appropriate variables else, return without calculating
        # use a set to check if all variables are in a given list easily
        requiredVariablesB = set(['DX', 'DY', 'DPX', 'DPY', 'ALFX', 'ALFY', 'BETX', 'BETY'])
        if not requiredVariablesB.issubset(self.columns):
            return
        requiredVariablesH = set(['SIGE', 'EX', 'EY'])
        if not requiredVariablesH.issubset(self.header.keys()):
            return
        
        # get indices to the columns we'll need in the data
        dxindex   = self.ColumnIndex('DX')
        dyindex   = self.ColumnIndex('DY')
        dpxindex  = self.ColumnIndex('DPX')
        dpyindex  = self.ColumnIndex('DPY')
        alfxindex = self.ColumnIndex('ALFX')
        alfyindex = self.ColumnIndex('ALFY')
        betxindex = self.ColumnIndex('BETX')
        betyindex = self.ColumnIndex('BETY')

        # constants
        sige = self.header['SIGE']
        beta = self.header['BETA'] # relativistic beta
        ex   = self.header['EX']
        ey   = self.header['EY']
        self.columns.extend(['SIGMAX', 'SIGMAY', 'SIGMAXP', 'SIGMAYP'])
        for elementname in self.sequence:
            # beam size calculations (using relation deltaE/E = beta^2 * deltaP/P)
            d = self.data[elementname]
            xdispersionterm = (d[dxindex] * sige / beta)**2
            ydispersionterm = (d[dyindex] * sige / beta)**2
            sigx = _np.sqrt((d[betxindex] * ex) + xdispersionterm)
            sigy = _np.sqrt((d[betyindex] * ey) + ydispersionterm)
            d.append(sigx)
            d.append(sigy)

            # beam divergences (using relation x',y' = sqrt(gamma_x,y * emittance_x,y))
            gammax = (1.0 + d[alfxindex]**2) / d[betxindex] # twiss gamma
            gammay = (1.0 + d[alfyindex]**2) / d[betyindex]
            xdispersionterm = (d[dpxindex] * sige / beta)**2
            ydispersionterm = (d[dpyindex] * sige / beta)**2
            sigxp  = _np.sqrt((gammax * ex) + xdispersionterm)
            sigyp  = _np.sqrt((gammay * ey) + ydispersionterm)
            d.append(sigxp)
            d.append(sigyp)

    def __repr__(self):
        s =  ''
        s += 'pymadx.Tfs instance\n'
        s += str(self.nitems) + ' items in lattice\n'
        return s

    def __len__(self):
        return len(self.sequence)

    def __iter__(self):
        self._iterindex = -1
        return self

    def next(self):
        if self._iterindex == len(self.sequence)-1:
            raise StopIteration
        self._iterindex += 1
        return self.GetRowDict(self.sequence[self._iterindex])

    def __getitem__(self,index):
        #index can be a slice object, string or integer - deal with in this order
        #return single item or slice of lattice
        if type(index) == slice:
            start,stop,step = index.start, index.stop, index.step #note slices are immutable
            #test values incase of ':' use
            if step != None and type(step) != int:
                raise ValueError("Invalid step "+step)
            if start != None and stop != None and step != None:
                # [start:stop:step]
                start = self._EnsureItsAnIndex(start)
                stop  = self._EnsureItsAnIndex(stop)
            elif start != None and stop != None and step == None:
                # [start:stop]
                start = self._EnsureItsAnIndex(start)
                stop  = self._EnsureItsAnIndex(stop)
                step  = 1
            elif start == None and stop == None and step > 0:
                # [::step]
                start = 0
                stop  = len(self)
            elif start == None and stop == None and step < 0:
                # [::-step]
                start = len(self) - 1
                stop  = -1 # range limit needs to be past 0
            elif start != None and stop == None and step > 0:
                # [start::step]
                start = self._EnsureItsAnIndex(start)
                stop  = len(self)
            elif start != None and stop == None and step == None:
                # [start::]
                start = self._EnsureItsAnIndex(start)
                stop  = len(self)
                step  = 1
            elif start != None and stop == None and step < 0:
                # [start::-step]
                start = self._EnsureItsAnIndex(start)
                stop  = -1
            elif start == None and stop != None and step > 0:
                # [:stop:step]
                start = 0
                stop  = self._EnsureItsAnIndex(stop)
            elif start == None and stop != None and step == None:
                # [:stop]
                start = 0
                stop  = self._EnsureItsAnIndex(stop)
                step  = 1
            elif start == None and stop != None and step < 0:
                # [:stop:-step]
                start = 0
                stop  = self._EnsureItsAnIndex(stop)
            index = slice(start,stop,step)
            #construct and return a new instance of the class
            a = Tfs()
            a._CopyMetaData(self)

            # whether to prepare new s coordinates as extra entry
            prepareNewS = False
            sOffset     = 0
            if start > 0 and 'S' in self.columns:
                prepareNewS = True
                # note S is at the end of an element, so take the element before for offset ( start - 1 )
                # if 'S' is in the columns, 'SORIGINAL' will be too
                sOffset = self.GetRowDict(self.sequence[start-1])['SORIGINAL']
                sOffsetMid = self.GetRowDict(self.sequence[start-1])['SMID']
            # prepare S coordinate and append to each list per element
            for i in range(index.start,index.stop,index.step):
                elementlist = list(self.data[self.sequence[i]]) # copy instead of modify existing
                if prepareNewS:
                    # maintain the original s from the original data
                    elementlist[self.ColumnIndex('S')] = elementlist[self.ColumnIndex('SORIGINAL')] - sOffset
                    elementlist[self.ColumnIndex('SMID')] = elementlist[self.ColumnIndex('SMID')] - sOffsetMid
                a._AppendDataEntry(self.sequence[i], elementlist)                
            return a
        
        elif type(index) == int:
            return self.GetRowDict(self.sequence[index])
        elif type(index) == str:
            return self.GetRowDict(index)
        else:
            raise ValueError("argument not an index or a slice")
    
    def _CheckName(self,name):
        if self.data.has_key(name):
            #name already exists - boo degenerate names!
            i = 1
            basename = name
            while self.data.has_key(name):
                name = basename+'_'+str(i)
                i = i + 1
            return name
        else:
            return name

    def _CopyMetaData(self,instance):
        params = ["header","columns","formats","filename"]
        for param in params:
            setattr(self,param,getattr(instance,param))
        #calculate the maximum s position - could be different based on the slice
        if 'S' in instance.columns:
            self.smax = instance[-1]['S']
        else:
            self.smax = 0

    def _DeepCopy(self,instance):
        #return type(self)(deepcopy(instance))
        self._CopyMetaData(instance)
        params = ["index","data","sequence","nitems","nsegments"]
        for param in params:
            setattr(self,param,_copy.deepcopy(getattr(instance,param)))

    def _AppendDataEntry(self,name,entry):
        if len(self.index) > 0:                   #check if there's any elements yet
            self.index.append(self.index[-1] + 1) #create an index
        else:
            self.index.append(0)
        self.sequence.append(name)  #append name to sequence
        self.nitems    += 1         #increment nitems
        self.data[name] = entry     #put the data in

    def __iadd__(self, other):
        self._CopyMetaData(other) #fill in any data from other instance
        for i in range(len(other)):
            key = other.sequence[i]
            self._AppendDataEntry(key,other.data[key])
        return self
            
    def NameFromIndex(self,index):
        """
        NameFromIndex(integerindex)

        return the name of the beamline element at index
        """
        return self.sequence[index]

    def NameFromNearestS(self,S) : 
        """
        NameFromNearestS(S) 

        return the name of the beamline element clostest to S 
        """
        
        i = self.IndexFromNearestS(S) 
        return self.sequence[i]

    def IndexFromNearestS(self,S) : 
        """
        IndexFromNearestS(S) 

        return the index of the beamline element clostest to S 
        """
        sMid = self.GetColumn('SMID')
        a = min(sMid, key=lambda x:abs(x-S))
        return int(_np.where(sMid == a)[0])

    def _EnsureItsAnIndex(self, value):
        if type(value) == str:
            return self.IndexFromName(value)
        else:
            return value

    def IndexFromName(self,namestring):
        """
        Return the index of the element named namestring

        """
        return self.sequence.index(namestring)

    def ColumnIndex(self,columnstring):
        """
        Return the index to the column matching the name
        
        REMEMBER: excludes the first column NAME
        0 counting

        """
        return self.columns.index(columnstring)

    def GetColumn(self,columnstring):
        """
        Return a numpy array of the values in columnstring in order
        as they appear in the beamline
        """
        i = self.ColumnIndex(columnstring)
        return _np.array([self.data[name][i] for name in self.sequence])

    def GetColumnDict(self,columnstring):
        """
        GetColumnDict(columnstring)
        return all data from one column in a dictionary

        note not in order
        """
        i = self.ColumnIndex(columnstring)
        d = dict((k,v[i]) for (k,v) in self.data.iteritems())
        #note we construct the dictionary comprehension in a weird way
        #here because SL6 uses python2.6 which doesn't have dict comprehension
        return d

    def GetRow(self,elementname):
        """
        Return all data from one row as a list
        """
        try:
            d = self[elementname]
        except KeyError:
            print 'No such item',elementname,' in this tfs file'
            return None
        return [d[key] for key in self.columns]
    
    def GetRowDict(self,elementname):
        """
        Return a dictionary of all parameters for a specifc element
        given by element name.

        note not in order
        """
        #no dictionary comprehension in python2.6 on SL6
        d = dict(zip(self.columns,self.data[elementname]))
        return d

    def GetSegment(self,segmentnumber):
        a = Tfs()
        a._CopyMetaData(self)
        segmentindex = self.columns.index('SEGMENT')
        hasname = 'NAME' in self.columns
        for key in self.sequence:
            if self.data[key][segmentindex] == segmentnumber:
                a._AppendDataEntry(key,self.data[key])
        return a

    def InterrogateItem(self,itemname):
        """
        InterrogateItem(itemname)
        
        Print out all the parameters and their names for a 
        particlular element in the sequence identified by name.
        """
        for i,parameter in enumerate(self.columns):
            print parameter.ljust(10,'.'),self.data[itemname][i]

    def GetElementNamesOfType(self,typename):
        """
        GetElementNamesOfType(typename) 
        
        Returns a list of the names of elements of a certain type. Typename can 
        be a single string or a tuple or list of strings.

        Examples: 
        >>> GetElementsOfType('SBEND')
        >>> GetElementsOfType(['SBEND','RBEND'])
        >>> GetElementsOfType(('SBEND','RBEND','QUADRUPOLE'))

        """
        if 'KEYWORD' in self.columns:
            i = self.ColumnIndex('KEYWORD')
        elif 'APERTYPE' in self.columns:
            i = self.ColumnIndex('APERTYPE')
        else:
            i = 0
        return [name for name in self.sequence if self.data[name][i] in typename]

    def GetElementsOfType(self,typename):
        """
        Returns a Tfs instance containing only the elements of a certain type.
        Typename can be a sintlge string or a tuple or list of strings.

        This returns a Tfs instance with all the same capabilities as this one.
        """
        names = self.GetElementNamesOfType(typename)
        a = Tfs()
        a._CopyMetaData(self)
        for key in names:
            a._AppendDataEntry(key,self.data[key])
        return a

    def ReportPopulations(self):
        """
        Print out all the population of each type of
        element in the beam line (sequence)
        """
        print 'Filename >',self.filename
        print 'Total number of items >',self.nitems
        if 'KEYWORD' in self.columns:
            i = self.ColumnIndex('KEYWORD')
        elif 'APERTYPE' in self.columns:
            i = self.ColumnIndex('APERTYPE')
        else:
            raise KeyError("No keyword or apertype columns in this Tfs file")
        
        keys = set([self.data[name][i] for name in self.sequence])
        populations = [(len(self.GetElementsOfType(key)),key) for key in keys]
        print 'Type'.ljust(15,'.'),'Population'
        for item in sorted(populations)[::-1]:
            print item[1].ljust(15,'.'),item[0]

    def Plot(self,filename='optics.pdf'):
        _Plot.PlotTfsBeta(self,outputfilename=filename)

    def PlotSimple(self,filename='optics.pdf'):
        _Plot.PlotTfsBeta(self,outputfilename=filename,machine=False)

    def IndexFromGmadName(self, gmadname, verbose=False):
        '''
        Returns the indices of elements which match the supplied gmad name.
        Useful because tfs2gmad strips punctuation from the component names, and irritating otherwise to work back.
        When multiple elements of the name match, returns the indices of all the components in a list.
        Arguments:
        gmadname     :    The gmad name of a component to search for.
        verbose      :    prints out matching name indices and S locations.  Useful for discriminating between identical names.
        '''
        indices = []
        #Because underscores are allowed in gmad names:
        punctuation = _string.punctuation.replace('_', '')
        for index, element in enumerate(self):
            #translate nothing to nothing and delete all forbidden chars from name.
            name = element['NAME']
            strippedName = name.translate(_string.maketrans("",""), punctuation)
            if _re.match(gmadname + "_?[0-9]*", strippedName):
                indices.append(index)
        if verbose:
            for index in indices:
                sPos = self.data[self.NameFromIndex(index)][self.ColumnIndex('S')]
                print " matches at S =", sPos, "@index", index
        if len(indices) == 1:
            return indices[0]
        elif len(indices) > 1:
            return indices
        else:
            raise ValueError(gmadname + ' not found in list')

    @staticmethod
    def GetSixTrackAperType(aper1,aper2,aper3,aper4):

        if aper1 == 0 and aper2 == 0 and aper3 == 0 and aper4== 0:
            return ''
        elif aper1 == aper3 and aper2 == aper4:
            return 'ELLIPSE'
        elif aper1 == aper3 and aper2 < aper4:
            return 'LHCSCREEN'
        elif aper1 < aper3 and aper2 == aper4:
            return 'LHCSCREEN'
        elif aper1 == 0 and aper2 == 0:
            return 'RACETRACK'
        elif aper3 == 0:
            return 'RECTANGLE'
        else:
            print "WARNING: The given aperture is not classified among the known types"
            print "A1=" + str(aper1) + " A2=" +  str(aper2) + " A3=" + str(aper3) + " A4=" + str(aper4)


def Cast(string):
    """
    Cast(string)
    
    tries to cast to a (python) float and if it doesn't work, 
    returns a string

    """
    try:
        return float(string)
    except ValueError:
        return string.replace('"','')
