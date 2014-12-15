import Ptc as _Ptc 
from TfsArray import TfsArray as _TfsArray

class PtcAnalysis(object) : 
    def __init__(self,ptcInput = None, ptcOutput = None) : 

        # Load input rays 
        if type(ptcInput) == str : 
            self.ptcInput = _Ptc.LoadInrays(ptcInput)
        else : 
            self.ptcInput = ptcInput 

        # Load output rays 
        if type(ptcOutput) == str : 
            self.ptcOutput = _TfsArray(ptcOutput)
        else : 
            self.ptcOutput = ptcOutput
    
    def SamplerLoop(self) : 
        for isampler in (0,self.ptcOutput.isegment,1) : 
            samplerData = self.ptcOutput.GetSegment(isampler) 
            
            xrms  = samplerData.GetColumn('X').std()
            yrms  = samplerData.GetColumn('Y').std()
            pxrms = samplerData.GetColumn('PX').std()
            pyrms = samplerData.GetColumn('PY').std()

            print isampler, xrms, pxrms, yrms, pyrms
            
        
