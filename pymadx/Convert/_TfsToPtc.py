import pymadx.Beam as _Beam
import pymadx.Builder as _Builder
import numpy as _np
import re as _re
import csv

import pymadx.Data as _Data

def TfsToPtc(inputfile,outputfilename, ptcfile, startname=None,
             stopname=None,ignorezerolengthitems=True,samplers='all',
             beampiperadius=0.2,beam=True,ptctrackaperture=[]):
    """
    Prepare a madx model for PTC from a Tfs file containing the full
    twiss output from MADX.

    """

    madx = _Data.CheckItsTfs(inputfile)
    ptcfilename = ptcfile
        
    nitems = madx.nitems
    opencollimatorsetting = beampiperadius

    # data structures for checks
    angtot = 0.0
    lentot = 0.0
    lldiff = []
    dldiff = {}
    itemsomitted = []

    a = _Builder.Machine()
    
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

    requiredColumns = ['L', 'ANGLE', 'KSI', 'K0L', 'K0SL', 'K1L', 'K2L', 'K3L','K4L','K5L','K6L',
                       'K1SL', 'K2SL','K3SL','K4SL','K5SL','K6SL', 'TILT', 'KEYWORD',
                       'ALFX', 'ALFY', 'BETX', 'BETY', 'VKICK', 'HKICK', 'E1', 'E2', 'FINT', 'FINTX', 'HGAP']

    missing = [column for column in requiredColumns if column not in madx.columns]

    # raise a value error if a column is missing, otherwise the conversion will continue
    if len(missing) > 0:
        error = "Missing columns from tfs file - insufficient information to convert file\r\n"
        error += "Columns missing: "
        for column in missing:
            error += column + " "
        error += "\r\n"
        error += "Given columns  : "
        for index,column in enumerate(madx.columns):
            error += column
            if index != len(madx.columns)-1:
                error += ", "
        raise ValueError(error)

    # now assume all are columns present

    lindex          = madx.ColumnIndex('L')
    angleindex      = madx.ColumnIndex('ANGLE')
    ksIindex        = madx.ColumnIndex('KSI')
    k0lindex        = madx.ColumnIndex('K0L')
    k0slindex       = madx.ColumnIndex('K0SL')
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
    e1index         = madx.ColumnIndex('E1')
    e2index         = madx.ColumnIndex('E2')
    fintindex       = madx.ColumnIndex('FINT')
    fintxindex      = madx.ColumnIndex('FINTX')
    hgapindex       = madx.ColumnIndex('HGAP')
    h1index         = madx.ColumnIndex('H1')
    h2index         = madx.ColumnIndex('H2')

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
        tilt = madx.data[name][tiltindex]
        if tilt != 0:
            kws['tilt'] = tilt
        
        e1    = madx.data[name][e1index]
        e2    = madx.data[name][e2index]
        fint  = madx.data[name][fintindex]
        fintx = madx.data[name][fintxindex]
        hgap  = madx.data[name][hgapindex]
        k1l   = madx.data[name][k1lindex]
        h1    = madx.data[name][h1index]
        h2    = madx.data[name][h2index]

        if k1l:
            kws['k1'] = k1l / l

        

        if t == 'DRIFT':
            a.AddDrift(rname,l,**kws)

        elif t == 'QUADRUPOLE':
            k1 = madx.data[name][k1lindex] / l
            a.AddQuadrupole(rname,l,**kws)

        elif t == 'SEXTUPOLE':
            k2 = madx.data[name][k2lindex] / l
            a.AddSextupole(rname,l,k2=k2,**kws)

        elif t == 'OCTUPOLE':
            k3 = madx.data[name][k3lindex] / l
            a.AddOctupole(rname,l,k3=k3,**kws)

        elif t == 'SOLENOID':
            ks = madx.data[name][ksIindex] / l
            a.AddSolenoid(rname,l,ks=ks,**kws)

        elif t == 'SBEND':
            kws['e1'] = e1
            kws['fint'] = fint
            kws['e2'] = e2

            # in madx, -1 means fintx was allowed to default to fint and we should do the same
            # so if set to 0, this means we want it to be 0
            if fintx != -1:
                kws['fintx'] = fintx

            if h1 != 0:
                kws['h1'] = h1
            if h2 != 0:
                kws['h2'] = h2
            if hgap != 0:
                kws['hgap'] = hgap

            angle = madx.data[name][angleindex]
            a.AddDipole(rname,category='sbend',length=l,angle=angle,**kws)

        elif t == 'RBEND':
            angle = madx.data[name][angleindex]
            # set element length to be the chord length - tfs output rbend
            # length is arc length
            chordLength = l
            if angle != 0:
                chordLength = 2 * (l / angle) * _np.sin(angle / 2.)  # protect against 0 angle rbends
            # subtract dipole angle/2 added on to poleface angles internally by
            # madx
            poleInAngle = e1 - 0.5 * angle
            poleOutAngle = e2 - 0.5 * angle
            if poleInAngle != 0:
                kws['e1'] = poleInAngle
            if poleOutAngle != 0:
                kws['e2'] = poleOutAngle
            if fint != 0:
                kws['fint'] = fint
            # in madx, -1 means fintx was allowed to default to fint and we should do the same
            # so if set to 0, this means we want it to be 0
            if fintx != -1:
                kws['fintx'] = fintx

            if h1 != 0:
                kws['h1'] = h1
            if h2 != 0:
                kws['h2'] = h2
            if hgap != 0:
                kws['hgap'] = hgap

            a.AddDipole(rname,category='rbend',length=chordLength,angle=angle,**kws)

        elif t == 'MARKER':
            angle = madx.data[name][angleindex]
            a.AddMarker(rname, **kws)

        elif t == 'MULTIPOLE':
            kn0l  = madx.data[name][k0lindex]
            kn1l  = madx.data[name][k1lindex]
            kn2l  = madx.data[name][k2lindex]
            kn3l  = madx.data[name][k3lindex]
            kn4l  = madx.data[name][k4lindex]
            kn5l  = madx.data[name][k5lindex]
            kn6l  = madx.data[name][k6lindex]
            kn0sl = madx.data[name][k0slindex]
            kn1sl = madx.data[name][k1slindex]
            kn2sl = madx.data[name][k2slindex]
            kn3sl = madx.data[name][k3slindex]
            kn4sl = madx.data[name][k4slindex]
            kn5sl = madx.data[name][k5slindex]
            kn6sl = madx.data[name][k6slindex]

            a.AddMultipole(
                rname,
                knl=(kn0l, kn1l, kn2l, kn3l, kn4l, kn5l, kn6l),
                ksl=(kn0sl, kn1sl, kn2sl, kn3sl, kn4sl, kn5sl, kn6sl),
                **kws)
        elif t == 'HKICKER':
            hkick = madx.data[name][hkickangleindex]
            a.AddHKicker(rname, hkick=hkick, length=l)
        elif t == 'VKICKER':
            vkick = madx.data[name][vkickangleindex]
            a.AddVKicker(rname, vkick=vkick, length=l)
        elif t == 'TKICKER':
            vkick = madx.data[name][vkickangleindex]
            hkick = madx.data[name][hkickangleindex]
            a.AddTKicker(rname, vkick=vkick, hkick=hkick, length=l)
        else:
            print 'MadxTfs2Ptc> unknown element type: ',t,' for element named: ',name
            if not zerolength:
                print('MadxTfs2Ptc> replacing with drift')
                a.AddDrift(rname,l)
            else:
                pass

    a.AddSampler(samplers)
    a.AddPTCTrackAperture(ptctrackaperture)
    # Make beam file 
    if beam: 
        b = MadxTfsToPtcBeam(madx, ptcfilename, startname)
        a.AddBeam(b)

    a.Write(outputfilename)

    return a

def MadxTfsToPtcBeam(tfs, ptcfilename,  startname=None):
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

    beam  = _Beam.Beam(particle, energy,'ptc', emitx=ex, emity=ey, sigmaE=sigmae)

    beam.SetDistribFileName(ptcfilename) 

    return beam
