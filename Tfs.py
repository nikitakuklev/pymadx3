
class Tfs:
    """
    MADX Tfs file reader

    a = Tfs()
    a.Load('myfile.tfs')

    a has data members:
    
    header  - dictionary of header items
    columns - list of column names
    formats - list of format strings for each column
    data    - dictionary of entries in tfs file by name string

    NOTE: this assumes NAME is the first column

    databyindex - dictionary by integer index in sequence
    sequence    - list of names in the order they appear in the file
    nitems      - number of items in sequence

    Examples:

    a.data['IP.1'] #returns all entries (minus the name) for element IP.1
    a.databyindex[321] #returns item number 321 from beamline (0 counting)

    """
    def __init__(self,filename=None):
        self.header      = {}
        self.columns     = []
        self.formats     = []
        self.data        = {}
        self.databyindex = {}
        self.sequence    = []
        self.nitems      = 0
        if filename != None:
            self.Load(filename)
        
    def Clear(self):
        self.__init__()
    
    def Load(self,filename):
        """
        Load('filename.tfs')
        
        read the tfs file and prepare data structures
        """
        f = open(filename)

        for line in f:
            splitline = line.strip('\n').split()
            sl        = splitline #shortcut
            if line[0] == '@':
                #header
                self.header[sl[1]] = sl[-1].replace('"','')
            elif line[0] == '*':
                #name
                self.columns.extend(sl[2:]) #miss * and NAMES
            elif line[0] == '$':
                #format
                self.formats.extend(sl[2:]) #miss $ and NAMES
            else:
                #data
                d = [Cast(item) for item in sl]
                self.sequence.append(d[0]) # keep the name in sequence
                self.data[d[0]] = d[1:]    # put in data dict by name
                self.databyindex[self.nitems] = d
                self.nitems += 1 # keep tally of number of items
                
        f.close()

    def NameFromIndex(self,index):
        """
        NameFromIndex(integerindex)

        return the name of the beamline element at index
        """
        return self.sequence[index]

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

    def ColumnByName(self,columnstring):
        """
        Column(columnstring)
        return all data from one column

        returns a dictionary by name of item
        """
        i = self.ColumnIndex(columnstring)
        d = {k:v[i] for (k,v) in self.data.iteritems()}
        return d

    def ColumnByIndex(self,columnstring):
        """
        ColumnByIndex(columnstring)
        
        returns a list of the values in columnstring in order
        as they appear in the beamline

        """
        i = self.ColumnIndex(columnstring)
        return [self.data[name][i] for name in self.sequence]
        


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
