class Element : 
    def __init__() : 
        pass 

class Machine :     
    def __init__() : 
        pass

class ParamInput :
    def __init__(self, fileName) : 
        self.fileName = fileName 
        self.readFile()
        self.determineParam()

    def readFile(self) :
        f = open(self.fileName) 
        self.file = []
        for l in f : 
            self.file.append(l)
        
    def determineParam(self) : 
        for l in f : 
            pass
