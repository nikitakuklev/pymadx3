import tarfile
import numpy as _np

import Plot as _Plot

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
    def __init__(self,filename=None):
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
            self.DeepCopy(filename)
        
    def Clear(self):
        self.__init__()
    
    def Load(self,filename):
        """
        Load('filename.tfs')
        
        read the tfs file and prepare data structures
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

        self.index = range(0,len(self.data),1)
        if 'S' in self.columns:
            self.smax = self[-1]['S']
        else:
            self.smax = 0

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
            f = [a._AppendDataEntry(self.sequence[i],self.data[self.sequence[i]]) for i in range(index.start,index.stop,index.step)]
            del f
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
        self._CopyMetaData(instance)
        params = ["index","data","sequence","nitems","nsegments"]
        for param in params:
            setattr(self,param,getattr(instance,param))

    def _AppendDataEntry(self,name,entry):
        if len(self.index) > 0:                   #check if there's any elements yet
            self.index.append(self.index[-1] + 1) #create an index
        else:
            self.index.append(0)
        self.sequence.append(name)  #append name to sequence
        self.nitems    += 1         #increment nitems
        self.data[name] = entry     #put the data in
            
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
        s = self.GetColumn('S')
        l = self.GetColumn('L')

        #iterate over beamline and record element if S is between the
        #sposition of that element and then next one
        #note madx S position is the end of the element by default
        ci = [i for i in self.index[0:-1] if (S > s[i]-l[i] and S < s[i]+1e-7)]
        try:
            ci = ci[0] #return just the first match - should only be one
        except IndexError:
            #protect against S positions outside range of machine
            if S > s[-1]:
                ci =-1
            else:
                ci = 0
        #check the absolute distance to each and return the closest one
        #make robust against s positions outside machine range
        try:
            if abs(S-s[ci]) < abs(S-s[ci+1]) : 
                return ci 
            else : 
                return ci+1
        except IndexError:
            return ci

    def _EnsureItsAnIndex(self, value):
        if type(value) == str:
            return self.IndexFromName(value)
        else:
            return value

    def IndexFromName(self,namestring):
        """
        IndexFromName(namestring)

        return the index of the element named namestring

        """
        return self.sequence.index(namestring)

    def ColumnIndex(self,columnstring):
        """
        ColumnIndex(columnname):
        
        return the index to the column matching the name
        
        REMEMBER: excludes the first column NAME
        0 counting

        """
        return self.columns.index(columnstring)

    def GetColumn(self,columnstring):
        """
        GetColumn(columnstring)
        return a numpy array of the values in columnstring in order
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
        GetRow(elementname)
        return all data from one row as a list

        note
        """
        d = self[elementname]
        return [d[key] for key in self.columns]
    
    def GetRowDict(self,elementname):
        """
        ElementDict(elementname)
        return a dictionary of all parameters for a specifc element
        given by element name

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
        
        Print out all the parameters and their
        names for a particlular element in the 
        sequence identified by name
        """
        for i,parameter in enumerate(self.columns):
            print parameter.ljust(10,'.'),self.data[itemname][i]

    def GetElementsOfType(self,typename) :
        """
        GetElementsOfType(typename) 
        
        Returns a list of the names of elements of a certain type

        typename can be a single string or a tuple or list of strings

        ie 
        GetElementsOfType('SBEND')
        GetElementsOfType(['SBEND','RBEND'])
        GetElementsOfType(('SBEND','RBEND','QUADRUPOLE'))

        """
        if 'KEYWORD' in self.columns:
            i = self.ColumnIndex('KEYWORD')
        elif 'APERTYPE' in self.columns:
            i = self.ColumnIndex('APERTYPE')
        else:
            i = 0
        return [name for name in self.sequence if self.data[name][i] in typename]

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
        _Plot.PlotTfsBetaSimple(self,outputfilename=filename)


def Cast(string):
    """
    Cast(string)
    
    tries to cast to a (python)float and if it doesn't work, 
    returns a string

    """
    try:
        return float(string)
    except ValueError:
        return string.replace('"','')
