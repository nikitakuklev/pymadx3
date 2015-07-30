import pymadx as _pymadx
import numpy as _np
import re as _re

def MadxTfs2Ptc(input,outputfilename,startname=None,stopname=None,ignorezerolengthitems=True,samplers='all',beampiperadius=0.2,beam=True,usemadxaperture=False) :

    if type(input) == str :
        print 'MadxTfs2Ptc> Loading file using pymadx'
        madx   = _pymadx.Tfs(input)
    else :
        print 'Already a pymadx instance - proceeding'
        madx   = input

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
        """
        # APERTURE
        # check if aperture info in tfs file
        # only use this if aperture info not specified in aperture dict
        if ( usemadxaperture and (name not in aperturedict) ):
            if 'APER_1' in madx.columns and 'APER_2' in madx.columns:
                #elliptical aperture
                aperX = madx.GetRowDict(name)['APER_1']
                aperY = madx.GetRowDict(name)['APER_2']
                if (aperX > 1e-6) and (aperY > 1e-6):
                    #both apertures must be specified for elliptical
                    kws['aper1'] = aperX #make sure it's non zero
                    kws['aper2'] = aperY 
                elif (aperX > 1e-6):
                    #resort to circular
                    kws['aper1'] = aperX #make sure it's non zero
                else:
                    pass
            elif 'APER_1' in madx.columns:
                #circular aperture
                aper = madx.GetRowDict(name)['APER_1']
                if aper > 1e-6:
                    kws['aper1'] = aper #make sure it's non zero

        # check if aperture info in aperture dict
        if name in aperturedict:
            #for now only 1 aperture - circular
            ap = (aperturedict[name],'m')
            if ap[0] < 1e-6:
                ap = (defaultbeampiperadius,'m')
            if t != 'RCOLLIMATOR':
                kws['aper'] = ap
        """

        if t == 'DRIFT':
            a.AddDrift(rname,l,**kws)


        elif t == 'QUADRUPOLE':
            k1 = madx.data[name][k1lindex] / l
            a.AddQuadrupole(rname,l,k1=k1,**kws)

        else:
            print 'unknown element type: ',t,' for element named: ',name
            print 'putting drift in instead as it has finite length'
            a.AddDrift(rname,l)


    a.AddSampler(samplers)


    # Make beam file 
    if beam: 
        b = MadxTfs2PtcBeam(madx, startname)
        a.AddBeam(b)

    a.WriteLattice(outputfilename)

    return a


def MadxTfs2PtcBeam(tfs, startname=None):
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
 #  particle = tfs.header['PARTICLE']      ##FIX THIS STUFF!
    particle = 'proton' 
    ex       = tfs.header['EX']
    ey       = tfs.header['EY']
    sigmae   = float(tfs.header['SIGE'])
    sigmat   = float(tfs.header['SIGT'])

    data     = tfs.GetRowDict(tfs.sequence[startindex])

    ptc = _pymadx.Ptc.GaussGenerator(ex,data['BETX'],data['ALFX'],ey,data['BETY'],data['ALFY'],sigmat,sigmae)

    ptc.Generate(1000,'inrays.madx')   ##Fix this thing

    beam  = _pymadx.Beam(particle,energy,'ptc')

    beam.SetDistribFileName('inrays.madx') 

    return beam

    
