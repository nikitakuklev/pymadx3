import pylab as pl
class Tfs :
    def __init__(self, fileName) :
        self.fileName = fileName
        self.header   = dict() 
        self.dataName = list()
        self.dataType = list()
        self.data     = dict()
        
        self.readFile(fileName) 

    def readFile(self, fileName) :
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
            self.data[v] = pl.array(self.data[v])            
