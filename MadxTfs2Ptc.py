import pymadx as _pymadx


def MadxTfs2Ptc(input) :

    if type(input) == str :
        print 'MadxTfs2Gmad> Loading file using pymadx'
        madx   = _pymadx.Tfs(input)
    else :
        print 'Already a pymadx instance - proceeding'
        madx   = input
        
    
