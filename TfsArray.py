import tarfile 
from Tfs import Cast 
import numpy as _numpy

class TfsArray : 

    def __init__(self,filename=None) : 
        self.header  = {}
        self.columns = [] 
        self.formats = [] 
        self.segment = [] 
        self.data    = []
        self.nitems  = 0
        self.filename= filename
        if self.filename != None : 
            self.Load(self.filename) 


    def Clear(self) :
        """ 
        Clear() 
        empty all internal variables 
        """
        self.__init__()

    def Load(self,filename) :
        """
        Load('filename.tfs')        
        read the tfs file and prepare data structures
        """

        # open gz file 
        if 'gz' in filename :
            print 'pymadx.TfsArray.Load> zipped file'
            tar = tarfile.open(filename,'r')
            f = tar.extractfile(tar.firstmember)
        else:
            print 'pymadx.TfsArray> normal file'
            f = open(filename)


        isegment = -1
        self.columns.append('SEGMENT')
        self.formats.append('%d')

        for line in f :
            sl = line.strip('\n').split()
            if line[0] == "@" : 
                # header
                # print 'pymadx.TfsArray> header',line 
                self.header[sl[1]] = sl[-1].replace('"','')
            elif line[0] == '*' : 
                # column name 
                # print 'pymadx.TfsArray> columns',line 
                self.columns.extend(sl[2:]) #miss * and NAMES                
            elif line[0] == '$' : 
                # column type
                # print 'pymadx.TfsArray> type',line 
                self.formats.extend(sl[2:]) #miss $ and NAMES                
            elif sl[0] == '#segment' : 
                # entry marker 
                # print 'pymadx.TfsArray> marker',line, self.nitems,isegment
                isegment=isegment+1
                
            else :                 
                # data
                d = [Cast(item) for item in sl]
                d.insert(0,isegment) 
                self.data.append(d)    # put in data dict by name
                self.nitems += 1 # keep tally of number of items                

            
        # make numpy array for convenience
        self.dataArray = _numpy.array(self.data)
            
        def GetColumn(self, colname) : 
            pass 

        def GetRow(self, rowindex) : 
            pass 

        def GetSegment(self, segmentindex) : 
            pass 

