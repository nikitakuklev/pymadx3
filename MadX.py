import pylab as _pl

class Tfs :
    '''class Tfs
       Tape file system data object  
       Tape.header : is a dictionary of header keys and values 
       Tape.dataName : column names 
       Tape.dataType : tfs column data type 
       Tape.data     : dictionary of data'''

    def __init__(self, fileName) :
        '''fileName is tfs file'''        
        self.fileName = fileName
        self.header   = dict() 
        self.dataName = list()
        self.dataType = list()
        self.data     = dict()
        
        self.readFile(fileName) 

    def readFile(self, fileName) :
        '''read tfs file'''
        f = open(fileName,'r')
        
        # loop over all lines in file
        for l in f :
            # tokenize line
            l = l.strip('\n')
            t = l.split()
            
            # check for header 
            if t[0] == '@' : 
                key = t[1]
                typ = t[2]
                if typ[-1] == 's' : 
                    i = l.find(t[3]) 
                    val = l[i:-1].strip('"')
                elif typ == '%le' : 
                    val = float(t[3])
                self.header[key] = val
            # check for name line
            elif t[0] == '*' :
                t = l.strip().split()
                int = 1 
                for v in t[1:] : 
                    self.dataName.append(v)
                    self.data[v] = list()
                    int = int+1
            # check for type line
            elif t[0] == '$' : 
                t = l.strip().split() 
                for v in t[1:] : 
                    self.dataType.append(v)
            # data
            else : 
                t = l.strip('\n').split()
                int = 0
                for v in t : 
                    if self.dataType[int] == '%le' : 
                        self.data[self.dataName[int]].append(float(v.strip('"')))
                    else : 
                        self.data[self.dataName[int]].append(v.strip('"'))
                        
                    int = int + 1
                        
        # Convert to array
        for v in self.dataName : 
            self.data[v] = _pl.array(self.data[v])            

class Common : 
    '''class Common 
       Class to extract information from madx output    
    '''
    def __init__(self) :
        '''Requires no arguments'''
        self._ind = _pl.arange(0,len(self.data[self.data.keys()[0]]),1)

    def findRowString(self, name, column = 'NAME') : 
        '''Find indicies of name in column, 
           eg Common.findRowString('MQXA.1R1..1','NAME') 
           eg Common.findRowString('MULTIPOLE','KEYWORD')''' 
        return self._ind[self.data[column] == name]

    def getRowIndicies(self, ind, column = 'NAME') : 
        '''Find indicies of name in column, 
           eg i = Common.findRowString('MULTIPOLE','KEYWORD')
           eg n = Common.getRowIndices(i,'NAME')'''
        return self.data[column][ind]

    def getUnique(self, column) : 
        '''Find unique values a column 
           eg Common.getUnique('KEYWORD') '''
        return _pl.unique(self.data[column])

class Twiss(Common,Tfs) : 
    '''class Twiss(Common,Tfs)
       Twiss data storage object
       Twiss.data is a dictionary containing numpy.arrays of the twiss output of madX'''

    def __init__(self, fileName) : 
        '''fileName is a madX twiss output file
           eg t = MadX.Twiss("./test/LHC/HL/madx_optics_beta1.5m/twiss_b1.data.thin")'''
        
        Tfs.__init__(self,fileName)
        Common.__init__(self)
    
class Survey : 
    def __init__(self, fileName) :
        pass

