import Ptc as _Ptc 
from TfsArray import TfsArray as _TfsArray
from Tfs import Tfs as _Tfs
import numpy as _np
import csv
import time

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
            #self.ptcOutput = _Tfs(ptcOutput)
        else : 
            self.ptcOutput = ptcOutput
    
    def SamplerLoop(self):
        #for segment in ptcOutput.segments:
        for isampler in (0,self.ptcOutput.isegment,1):
            #samplerData = self.ptcOutput.GetSegment(segment)
            samplerData = self.ptcOutput.GetSegment(isampler)
            
            xrms  = samplerData.GetColumn('X').std()
            yrms  = samplerData.GetColumn('Y').std()
            pxrms = samplerData.GetColumn('PX').std()
            pyrms = samplerData.GetColumn('PY').std()

            print isampler, xrms, pxrms, yrms, pyrms

    def CalculateOpticalFunctions(self, output):
        """
        Calulates optical functions from a PTC output file
    
        output - the name of the output file
        """
        S      = []
        emittx = []
        emitty = []
        betx   = []
        bety   = []
        alphx  = []
        alphy  = []


        
        #for segment in ptcOutput.segments:
        for isampler in range(0,self.ptcOutput.isegment,1):
            #samplerData = self.ptcOutput.GetSegment(segment)
            samplerData = self.ptcOutput.GetSegment(isampler)
            print 'segment:', (isampler+1) ,'/', self.ptcOutput.isegment
        
            x  = samplerData.GetColumn('X')
            y  = samplerData.GetColumn('Y') 
            xp = samplerData.GetColumn('PX')
            yp = samplerData.GetColumn('PY')
            s  = samplerData.GetColumn('S')
        
            #Calculate sums
            s_s    = _np.sum(s)
            x_s    = _np.sum(x)
            y_s    = _np.sum(y)
            xp_s   = _np.sum(xp)
            yp_s   = _np.sum(yp)
            xx_s   = _np.sum(x*x)
            xxp_s  = _np.sum(x*xp)
            xpxp_s = _np.sum(xp*xp)    
            yy_s   = _np.sum(y*y)
            yyp_s  = _np.sum(y*yp)
            ypyp_s = _np.sum(yp*yp)

            wgt   = len(x)

            #normalise
            s_s    /= wgt
            x_s    /= wgt
            y_s    /= wgt
            xp_s   /= wgt
            yp_s   /= wgt
            xx_s   /= wgt
            xxp_s  /= wgt
            xpxp_s /= wgt    
            yy_s   /= wgt
            yyp_s  /= wgt
            ypyp_s /= wgt
            
            x_sv  = _np.sum(x-_np.mean(x))
            xx_sv = _np.sum((x-_np.mean(x))*(x-_np.mean(x)))
            y_sv  = _np.sum(y-_np.mean(y))
            yy_sv = _np.sum((y-_np.mean(y))*(y-_np.mean(y)))
            
            #Calculate variances/sigmas
            variance_x = (xx_sv - (x_sv * x_sv)/wgt)/wgt
            variance_y = (yy_sv - (y_sv * y_sv)/wgt)/wgt
            sigma_x    = _np.sqrt(variance_x)
            sigma_y    = _np.sqrt(variance_y)
            variance_xp = (xpxp_s - (xp_s * xp_s)/wgt)/wgt
            variance_yp = (ypyp_s - (yp_s * yp_s)/wgt)/wgt
            sigma_xp   = _np.sqrt(variance_xp)
            sigma_yp   = _np.sqrt(variance_yp)
        
            #Calculate means
            x_m  = x_s/wgt
            y_m  = y_s/wgt
            xp_m = xp_s/wgt
            yp_m = yp_s/wgt
        
            #Calculate sigmas
            sigma_x_xp = xxp_s - xx_s * xp_s;
            sigma_y_yp = yyp_s - y_s * yp_s;
        
            #Calculate the moments using the sums
            xx_s   -= x_s*x_s
            xxp_s  -= x_s*xp_s
            xpxp_s -= xp_s*xp_s
            yy_s   -= y_s*y_s  
            yyp_s  -= y_s*yp_s
            ypyp_s -= yp_s*yp_s

            #Calculate emittance
            emitt_x = _np.sqrt(xx_s*xpxp_s - xxp_s*xxp_s)
            emitt_y = _np.sqrt(yy_s*ypyp_s - yyp_s*yyp_s)

            #Calculate optical functions
            beta_x  =  xx_s  / emitt_x;
            beta_y  =  yy_s  / emitt_y;
            alph_x  = -xxp_s / emitt_x;
            alph_y  = -yyp_s / emitt_y;

            ####Dispersion calculation and error calculations to be added
        
            S.append(s_s)
            emittx.append(emitt_x)
            emitty.append(emitt_y)
            betx.append(beta_x)
            bety.append(beta_y)
            alphx.append(alph_x)
            alphy.append(alph_y)

        with open(output,'w') as ofile:        
            writer=csv.writer(ofile, delimiter='\t',lineterminator='\n',)
            timestamp = time.strftime("%Y/%m/%d-%H:%M:%S")
            writer.writerow(['# ','Optical functions from PTC output', timestamp])
            writer.writerow(['S[m]','EX[m]','EY[m]','BETX[m]','BETY[m]','ALFX[m]','ALFY[m]'])
            for i in range(len(S)):
                row = [float("{0:.4e}".format(S[i])),float("{0:.4e}".format(emittx[i])),float("{0:.4e}".format(emitty[i]))]
                row.extend([float("{0:.4e}".format(betx[i])),float("{0:.4e}".format(bety[i]))])
                row.extend([float("{0:.4e}".format(alphx[i])),float("{0:.4e}".format(alphy[i]))])
                writer.writerow(row)
            
        
