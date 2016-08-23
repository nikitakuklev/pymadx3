import pymadx as _pymadx
import numpy as _np
import re as _re
import csv


def MadxTfs2Ptc(input,outputfilename, ptcfile, startname=None,stopname=None,ignorezerolengthitems=True,samplers='all',beampiperadius=0.2,beam=True) :

    if type(input) == str :
        print 'MadxTfs2Ptc> Loading file using pymadx'
        madx   = _pymadx.Tfs(input)
    else :
        print 'Already a pymadx instance - proceeding'
        madx   = input

    ptcfilename = ptcfile
        
    nitems = madx.nitems
    opencollimatorsetting = beampiperadius

    # data structures for checks
    angtot = 0.0
    lentot = 0.0
    lldiff = []
    dldiff = {}
    itemsomitted = []        


    a = _pymadx.Builder.Machine()
    
    #prepare index for iteration:
    if startname == None:
        startindex = 0
    elif type(startname) == int:
        startindex = startname
    else:
        startindex = madx.IndexFromName(startname)
    if stopname   == None:
        stopindex = nitems #this is 1 larger, but ok as range will stop at n-step -> step=1, range function issue
    elif type(stopname) == int:
        stopindex = stopname
    else:
        stopindex  = madx.IndexFromName(stopname)
    if stopindex <= startindex:
        print 'stopindex <= startindex'
        stopindex = startindex + 1

    try:
        lindex          = madx.ColumnIndex('L')
        angleindex      = madx.ColumnIndex('ANGLE')
        ksIindex        = madx.ColumnIndex('KSI')
        k1lindex        = madx.ColumnIndex('K1L')
        k2lindex        = madx.ColumnIndex('K2L')
        k3lindex        = madx.ColumnIndex('K3L')
        k4lindex        = madx.ColumnIndex('K4L')
        k5lindex        = madx.ColumnIndex('K5L')
        k6lindex        = madx.ColumnIndex('K6L')
        k1slindex       = madx.ColumnIndex('K1SL')
        k2slindex       = madx.ColumnIndex('K2SL')
        k3slindex       = madx.ColumnIndex('K3SL')
        k4slindex       = madx.ColumnIndex('K4SL')
        k5slindex       = madx.ColumnIndex('K5SL')
        k6slindex       = madx.ColumnIndex('K6SL')
        tiltindex       = madx.ColumnIndex('TILT')
        tindex          = madx.ColumnIndex('KEYWORD')
        alphaxindex     = madx.ColumnIndex('ALFX')
        alphayindex     = madx.ColumnIndex('ALFY')
        betaxindex      = madx.ColumnIndex('BETX')
        betayindex      = madx.ColumnIndex('BETY')
        vkickangleindex = madx.ColumnIndex('VKICK')
        hkickangleindex = madx.ColumnIndex('HKICK')
        
    except ValueError:
        print 'Missing columns from tfs file - insufficient information to convert file'
        print 'Required columns : L, ANGLE, KSI, K1L...K6L, K1SL...K6SL, TILT, KEYWORD, ALFX, ALFY, BETX, BETY, VKICK, HKICK'
        print 'Given columns    : '
        print madx.columns

        
    # iterate through input file and construct machine
    for i in range(startindex,stopindex):
        name = madx.sequence[i]
        #remove special characters like $, % etc 'reduced' name - rname
        rname = _re.sub('[^a-zA-Z0-9_]+','',name) #only allow alphanumeric characters and '_'
        t     = madx.data[name][tindex]
        l     = madx.data[name][lindex]
        ang   = madx.data[name][angleindex]
        if l <1e-9:
            zerolength = True
        else:
            zerolength = False

        if zerolength and ignorezerolengthitems:
            itemsomitted.append(name)
            continue #this skips the rest of the loop as we're ignoring this item

        kws = {} # element-specific keywords

        if t == 'DRIFT':
            a.AddDrift(rname,l,**kws)


        elif t == 'QUADRUPOLE':
            k1 = madx.data[name][k1lindex] / l
            a.AddQuadrupole(rname,l,k1=k1,**kws)

        elif t == 'SEXTUPOLE':
            k2 = madx.data[name][k2lindex] / l
            a.AddSextupole(rname,l,k2=k2,**kws)

        elif t == 'SBEND':
            angle = madx.data[name][angleindex]
            a.AddDipole(rname,category='sbend',length=l,angle=angle,**kws)

        elif t == 'RBEND':
            angle = madx.data[name][angleindex]
            a.AddDipole(rname,category='rbend',length=l,angle=angle,**kws)

        else:
            print 'unknown element type: ',t,' for element named: ',name
            print 'putting drift in instead as it has finite length'
            a.AddDrift(rname,l)


    a.AddSampler(samplers)


    # Make beam file 
    if beam: 
        b = MadxTfs2PtcBeam(madx, ptcfilename, startname)
        a.AddBeam(b)

    a.Write(outputfilename)

    return a


def MadxTfs2PtcBeam(tfs, ptcfilename,  startname=None):
    if startname == None:
        startindex = 0
    elif type(startname) == int:
        startindex = startname
    else:
        startindex = tfs.IndexFromName(startname)

    #MADX defines parameters at the end of elements so need to go 1 element
    #back if we can.

    if startindex > 0:
        startindex -= 1
    
    energy   = float(tfs.header['ENERGY'])
    gamma    = float(tfs.header['GAMMA'])
    particle = str.lower(tfs.header['PARTICLE'])
    ex       = tfs.header['EX']
    ey       = tfs.header['EY']
    sigmae   = float(tfs.header['SIGE'])
    sigmat   = float(tfs.header['SIGT'])

    data     = tfs.GetRowDict(tfs.sequence[startindex])

    beam  = _pymadx.Beam(particle, energy,'ptc', emitx=ex, emity=ey, sigmaE=sigmae)

    beam.SetDistribFileName(ptcfilename) 

    return beam


  

    
