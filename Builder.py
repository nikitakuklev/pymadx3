# pymadx.Builder - tools to build madx lattices
# Version 1.0
# S. T. Boogert
# stewart.boogert@rhul.ac.uk

import _General
from   _General import IsFloat as _IsFloat
from   decimal import Decimal as _Decimal
import time

"""
Builder

Build generic machines for madx. (Based on pybdsim.Builder)
You can create a lattice using one of the predefined simple 
lattices or by adding many pieces together of your own design. 
Finally, output the gmad files required.

Classes:
Element - beam line element that always has name and type
Machine - a list of elements

"""

bdsimcategories = [
    'drift',
    'quadrupole',
    ]

#*************************************************************************************************
class Element(dict) : 
    """
    Element - a beam element class - inherits dict

    Element(name,type,**kwargs)
    
    A beam line element must ALWAYs have a name, and type.
    The keyword arguments are specific to the type and are up to
    the user to specify.

    Numbers are converted to a python Decimal type to provide 
    higher accuracy in the representation of numbers - 15 
    decimal places are used. 
    """
    def __init__(self, name, category, **kwargs):
        if category not in bdsimcategories:
            raise ValueError("Not a valid BDSIM element type")
        self.name     = str(name)
        self.category = str(category)
        self.length      = 0.0 #for bookeeping only
        self['name']     = self.name
        self['category'] = self.category        
        self._keysextra = []
        for key,value in kwargs.iteritems():
            if type(value) == tuple and category != 'multipole':
                #use a tuple for (value,units)
                self[key] = (_Decimal(str(value[0])),value[1])
            elif type(value) == tuple and category == 'multipole' : 
                self[key] = value
            elif _IsFloat(value):
                #just a number
                self[key] = _Decimal(str(value))
            else:
                #must be a string
                self[key] = '"'+value+'"'
            self._keysextra.append(str(key)) #order preserving
        if 'l' in self:
            if type(self['l']) == tuple:
                ll = self['l'][0]
            else:
                ll = self['l']
            self.length += float(ll)

    def keysextra(self):
        #so behaviour is similar to dict.keys()
        return self._keysextra

    def __repr__(self):
        s = ''
        s += self.name + ': '
        s += self.category
        if len(self._keysextra) > 0:
            for key in self._keysextra:
                if type(self[key]) == tuple and self.category != 'multipole':
                    s += ', ' + key + '=' + str(self[key][0]) + '*' + str(self[key][1])
                elif type(self[key]) == tuple and self.category == 'multipole' : 
                    s += ', ' + key + '=' + '{'+(','.join([str(s) for s in self[key]]))+'}'
                else:
                    s += ', ' + key + '=' + str(self[key])
        s += ';\n'
        return s

#*************************************************************************************************
class Line(list):
    def __init__(self,name,*args):
        for item in args[0]:
            if type(item) != Element:
                raise TypeError("Line is a list of Elements")
        list.__init__(self,*args)
        self.name   = name
        self.length = 0.0 
        for item in args[0]:
            self.length += item.length
        
    def __repr__(self):
        s = ''
        for item in self:
            s += str(item)+'\n' #uses elements __repr__ function
        s += self.name+ ': line=('
        s += ', '.join([item.name for item in self]) + ');\n'
        return s

    def DefineConstituentElements(self):
        s = ''
        for item in self:
            s += str(item) #uses elements __repr__ function
        return s

#*************************************************************************************************
class Sampler:
    ''' PTC observe command ''' 
    def __init__(self,name):
        self.name = name

    def __repr__(self):
        return 'PTC_OBSERVE, place='+self.name+';\n'

#*************************************************************************************************
class Machine :     
    def __init__(self,verbose=False):
        self.verbose   = verbose
        self.sequence  = []
        self.elements  = []
        self.elementsd = {}
        self.samplers  = []
        self.length    = 0.0
        self.angint    = 0.0
        self.beam      = None

    def __repr__(self):
        s = ''
        s += 'pybdism.Builder.Machine instance\n'
        s += str(len(self.sequence)) + ' items in sequence\n'
        s += str(len(self.elements)) + ' unique elements defined\n'
        return s

    def __iter__(self):
        self._iterindex = -1
        return self

    def next(self):
        if self._iterindex == len(self.sequence)-1:
            raise StopIteration
        self._iterindex += 1
        return self.elementsd[self.sequence[self._iterindex]]
        
    def __getitem__(self,name):
        if _IsFloat(name):
            return self.elementsd[self.sequence[name]]
        else:
            return self.elementsd[name]

    def __len__(self):
        return len(self.elementsd.keys())

    def Append(self,object):
        if type(object) not in (Element,Line):
            raise TypeError("Only Elements or Lines can be added to the machine")
        elif object.name not in self.sequence:
            #hasn't been used before - define it
            if type(object) is Line:
                for element in object:
                    self.elements.append(element)
                    self.elementsd[element.name] = element
                self.elements.append(object)
                self.elementsd[object.name] = object
            else:
                self.elements.append(object)
                self.elementsd[object.name] = object
        #finally add it to the sequence
        self.sequence.append(object.name)
        self.length += object.length

    def WriteLattice(self,filename,verbose=False):
        if self.verbose or verbose:
            WriteLattice(self,filename,True)
        else:
            WriteLattice(self,filename,False)

    def AddDrift(self, name='dr', length=0.1, **kwargs):
        if self.verbose:
            print 'AddDrift>  ',name,' ',length,' ',kwargs
        if length < 1e-12:
            self.AddMarker(name)
        else:
            self.Append(Element(name,'drift',l=length,**kwargs))
          
    def AddQuadrupole(self, name='qd', length=0.1, k1=0.0, **kwargs):
        self.Append(Element(name,'quadrupole',l=length,k1=k1,**kwargs))

    def AddSampler(self,*elementnames):
        if elementnames[0] == 'all':
            for element in self.elements:
                #remember we can only have samplers on uniquely
                #named elements (for now)
                self.samplers.append(Sampler(element.name))
        elif elementnames[0] == 'first':
            self.samplers.append(Sampler(self.elements[0].name))
        elif elementnames[0] == 'last':
            self.samplers.append(Sampler(self.elements[-1].name))
        else:
            for element in elementnames[0]:
                if element not in self.elements:
                    raise ValueError(elementname+" is not a valid element in this machine")
                else:
                    self.samplers.append(Sampler(element))
    def AddBeam(self, beam=None) : 
        self.beam = beam

# General scripts below this point

#*************************************************************************************************
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

def WriteLattice(machine, filename, verbose=False):
    """
    WriteLattice(machine(machine),filename(string),verbose(bool))

    Write a lattice to disk. This writes several files to make the
    machine, namely:
    
    filename_components.madx - component files (max 10k per file)
    filename_sequence.madx   - lattice definition
    filename_samplers.madx   - sampler definitions (max 10k per file)
    filename.gmad            - suitable main file with all sub 
                               files in correct order

    these are prefixed with the specified filename / path

    """
    
    if not isinstance(machine,Machine):
        raise TypeError("Not machine instance")
    
    elementsperline = 100 #number of machine elements per bdsim line (not text line)
    
    #check filename
    if filename[-5:] != '.madx':
        filename += '.madx'
    #check if file already exists
    ofilename = filename
    filename = _General.CheckFileExists(filename)
    if filename != ofilename:
        print 'Warning, chosen filename already exists - using filename: ',filename.split('.')[0]
    basefilename = filename[:-5]#.split('/')[-1]

    #prepare names
    files         = []
    fn_main       = basefilename + '.madx'
    fn_components = basefilename + '_components.madx'
    fn_sequence   = basefilename + '_sequence.madx'
    fn_samplers   = basefilename + '_samplers.madx'
    fn_beam       = basefilename + '_beam.madx'
    fn_options    = basefilename + '_options.madx'
    timestring = '! ' + time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime()) + '\n'
    
    #write component files
    f = open(fn_components,'w')
    files.append(fn_components)
    f.write(timestring)
    f.write('! pymadx.Builder Lattice \n')
    f.write('! COMPONENT DEFINITION\n\n')
    for element in machine.elements:
        f.write(str(element))
    f.close()

    #write lattice sequence
    f = open(fn_sequence,'w')
    files.append(fn_sequence)
    f.write(timestring)
    f.write('! pymadx.Builder Lattice \n')
    f.write('! LATTICE SEQUENCE DEFINITION\n\n')
    sequencechunks = _General.Chunks(machine.sequence,elementsperline)
    linelist = []
    ti = 0
    for line in _General.Chunks(machine.sequence,elementsperline):
        f.write('l'+str(ti)+': line = ('+', '.join(line)+');\n')
        linelist.append('l'+str(ti))
        ti += 1
    # need to define the period before making sampler planes
    f.write('lattice: line = ('+', '.join(linelist)+');\n')
    f.write(machine.beam.ReturnBeamString())
    f.write('use, period=lattice;\n')
    f.close()

    # write beam 
    if machine.beam != None : 
        f = open(fn_beam,'w') 
        files.append(fn_beam)
        f.write(timestring) 
        f.write('! pymadx.Builder \n')
        f.write('! BEAM DEFINITION \n\n')
#        f.write(machine.beam.ReturnBeamString())
        f.write(machine.beam.ReturnPtcString())

    #write samplers
    if len(machine.samplers) > 0:
        f = open(fn_samplers,'w')
        files.append(fn_samplers)
        f.write(timestring)
        f.write('! pymadx.Builder Lattice \n')
        f.write('! SAMPLER DEFINITION\n\n')
        for sampler in machine.samplers:
            f.write(str(sampler))
        f.write('ptc_track, element_by_element, dump, turns=1, icase=5, onetable;')
        f.write('PTC_TRACK_END;')
        f.write('ptc_end;')
        f.close()

    # write main file
    f = open(fn_main,'w')
    f.write(timestring)
    f.write('! pymadx.Builder Lattice \n')
    f.write('! number of elements = ' + str(len(machine.elements)) + '\n')
    f.write('! total length       = ' + str(machine.length) + ' m\n\n')
    
    for fn in files:
        fn = fn.split('/')[-1]
        f.write("call, file='"+fn+"';\n")
    f.close()

    #user feedback
    print 'Lattice written to:'
    for fn in files:
        print(fn)
    print 'All included in main file: \n',fn_main