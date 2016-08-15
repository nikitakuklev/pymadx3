# pymadx.Beam - generate MADX beam
# Version 1.0
# S. T. Boogert
# stewart.boogert@rhul.ac.uk

MADXDistributionTypes = [
    'reference',
    'madx',
    'ptc'
]

MADXParticleTypes = [
    'electron',
    'positron',
    'proton'
]

class Beam(dict):
    def __init__(self,particletype='e-',energy=1.0,distrtype='reference',*args,**kwargs):
        dict.__init__(self,*args,**kwargs)
        self.isPTCDistribution = False
        self.SetParticleType(particletype)
        self.SetEnergy(energy)
        self.SetDistributionType(distrtype)

    def __repr__(self):
        return self.ReturnBeamString()

    def GetItemStr(self, key):
        return str(self[key])
        
    def SetParticleType(self,particletype='e-'):
        if particletype == 'e-' : 
            particletype = 'electron' 
        elif particletype == 'e+' : 
            particletype = 'positron' 
        elif particletype == 'proton' :
            particletype = 'proton'

        if particletype not in MADXParticleTypes:
            raise ValueError("Unknown particle type: '"+str(particletype)+"'")
        self['particle'] = str(particletype) 

    def SetEnergy(self,energy=1.0,unitsstring='GeV'):
        self['energy'] = str(energy)

    def SetDistributionType(self,distrtype='reference'):
        if distrtype not in MADXDistributionTypes:
            raise ValueError("Unknown distribution type: '"+str(distrtype)+"'")
        
        self['distrType'] = distrtype 
        if distrtype == 'madx':
            setattr(self, 'SetBetaX',            self._SetBetaX)
            setattr(self, 'SetBetaY',            self._SetBetaY) 
            setattr(self, 'SetAlphaX',           self._SetAlphaX)
            setattr(self, 'SetAlphaY',           self._SetAlphaY)
            setattr(self, 'SetEmittanceX',       self._SetEmittanceX) 
            setattr(self, 'SetEmittanceY',       self._SetEmittanceY)
            setattr(self, 'SetSigmaE',           self._SetSigmaE)
            setattr(self, 'SetSigmaT',           self._SetSigmaT)
        elif distrtype == 'ptc':
            self.isPTCDistribution = True
            setattr(self, 'SetDistribFileName',  self._SetDistribFileName)
        
    def ReturnBeamString(self):
        s = 'beam, particle='+self['particle']+', energy='+self['energy']
        s += ', ex=' + self.GetItemStr('emitx') + ', ey=' + self.GetItemStr('emity')
        if self.has_key('sigmaE'):
            s += ', sige=' + self.GetItemStr('sigmaE')+';\n'
        else:
            s += ';\n'
        return s

    def ReturnPtcString(self) : 
        s = 'ptc_create_universe;\n' 
        s+= 'ptc_create_layout,model=2,method=6,nst=10;\n'
        s+= 'call, file ="'+self['distrFile']+'";\n'
        s+= 'ptc_align;'
        return s
    
    def ReturnTwissString(self,basefilename='output'):
        s = 'twiss, save, '
        s += 'betx=' + self['betx'] + ', bety=' + self['bety']
        s += ', file=' + basefilename+'.tfs;'
        return s

    def SetT0(self,t0=0.0,unitsstring='s'):
        self['T0'] = t0 + '*' + unitsstring

    def _SetSigmaE(self,sigmae=0.001):
        """
        fractional energy spread
        """
        self['sigmaE'] = sigmae

    def _SetSigmaT(self,sigmat=1.0,unitsstring='um'):
        self['sigmaT'] = sigmat

    def _SetBetaX(self,betx=1.0,unitsstring='m'):
        self['betx'] = str(betx)# + '*' + unitsstring

    def _SetBetaY(self,bety=1.0,unitsstring='m'):
        self['bety'] = str(bety)# + '*' + unitsstring

    def _SetAlphaX(self,alphax=1.0,unitsstring='m'):
        self['alfx'] = str(alphax)# + '*' + unitsstring

    def _SetAlphaY(self,alphay=1.0,unitsstring='m'):
        self['alfy'] = str(alphay)# + '*' + unitsstring

    def _SetEmittanceX(self,emitx=1.0,unitsstring='um'):
        self['emitx'] = str(emitx)# + '*' + unitsstring
   
    def _SetEmittanceY(self,emity=1.0,unitsstring='um'):
        self['emity'] = str(emity)# + '*' + unitsstring

    def _SetDistribFileName(self, fileName) :
        self['distrFile'] = fileName
