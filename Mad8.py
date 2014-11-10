# http://mad.web.cern.ch/mad/madx.old/mad8tomadX/
# constant 
# multipole

import os as _os 

def ConvertDir(inputDir) : 
    files = _os.listdir(inputDir) 
    for f in files : 
        Mad8ToMadX(inputDir+'/'+f)
        
def Mad8ToMadX(inputName) : 
    inputFile  = open(inputName) 
    outputName  = inputName[inputName.rfind('/')+1:inputName.rfind('.')]+".xsifx"
    outputFile = open(outputName,'w')
    
    print 'Mad8ToMadX, input > ',inputName
    print 'Mad8ToMadX, output> ',outputName

    for l in inputFile : 
        l = l.rstrip()

        # find comments 
        ci = l.find('!')
        # find line continuations 
        ai = l.find('&')

        # if a continuation line is found 
        if ai != -1 :
            l     = l.replace('&',' ')
            ltc   = ' ' 
        else : 
            ltc   = ';'

        # Deal with each line
        if ci == -1 and len(l) == 0: # Empty line  
            pl = l
        elif ci == -1 and len(l) > 0 : # No comment and actual line 
            pl = l+ltc
        elif ci == 0 : # Whole line is comment
            pl = l 
        else : # comment present 
            if len(l) == 0 : 
                print ci
            # split line on comment 
            bcl = l[0:ci] # before comment
            acl = l[ci:]  # after comment
            pl  = bcl+ltc+acl
 

        #######################################################################################
        # Simple replacements 
        #######################################################################################
        # replace intr with intrument 
        if pl.find('INSTRUMENT') == -1 :
            pl = pl.replace('INST','INSTRUMENT')        
        # replace moni with monitor
        if pl.find('MONITOR') == -1 :
            pl = pl.replace('MONI','MONITOR')
        # replace mark with marker 
        if pl.find('MARKER') == -1 :
            pl = pl.replace('MARK','MARKER')
        # replace drif with drift 
        if pl.find('DRIFT') == -1 :
            pl = pl.replace('DRIF','DRIFT')
        # replace quad with quadrupole 
        if pl.find('QUADRUPOLE') == -1 :
            pl = pl.replace('QUAD','QUADRUPOLE') 
        # replace sext with sextupole 
        if pl.find('SEXTUPOLE') == -1 : 
            pl = pl.replace('SEXT','SEXTUPOLE')
        # replace octu with octupole
        if pl.find('OCTUPOLE') == -1 : 
            pl = pl.replace('OCTU','OCTUPOLE')
        # replace sben with sbend
        if pl.find('SBEND') == -1 :
            pl = pl.replace('SBEN','SBEND')
        # replace aper with aperture 
        if pl.find('APERTURE') == -1 :
            pl = pl.replace('APER','APERTURE') 
        # replce ecoll with ecollimator
        if pl.find('ECOLLIMATOR') == -1 :
            pl = pl.replace('ECOLL','ECOLLIMATOR') 
        # replce ecoll with ecollimator
        if pl.find('RCOLLIMATOR') == -1 :
            pl = pl.replace('RCOLL','RCOLLIMATOR') 

        #######################################################################################
        # Regular expressions 
        #######################################################################################
        # constant 

        # multipole 

        outputFile.write(pl+'\n')
