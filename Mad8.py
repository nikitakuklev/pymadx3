def Mad8ToMadX(inputName) : 
    inputFile  = open(inputName) 
    outputName  = inputName[0:inputName.rfind('.')]+".xsifx"
    outputFile = open(outputName,'w')
    
    print 'Mad8ToMadX, input > ',inputName
    print 'Mad8ToMadX, output> ',outputName

    for l in inputFile : 
        l = l.rstrip()

        # find comments 
        ci = l.find('!')
        ai = l.find('&')

        # if a continuation line is found 
        if ai != -1 :
            l     = l.replace('&',' ')
            ltc   = ' ' 
        else : 
            ltc   = ';'
        
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
        
        outputFile.write(pl+'\n')
