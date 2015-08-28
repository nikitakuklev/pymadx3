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
        sampler  = []
        S        = []
        betx     = []
        bety     = []
        alphx    = []
        alphy    = []
        dispx    = []
        dispy    = []
        dispxp   = []
        dispyp   = []
        emittx   = []
        emitty   = []
        sigmax   = []
        sigmay   = []
        sigmaxp  = []
        sigmayp  = []
        sigmaxxp = []
        sigmayyp = []
        meanx    = []
        meany    = []
        meanxp   = []
        meanyp   = []
        Wgt      = []

        
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
            E0 = samplerData.GetColumn('E')  #this is the specified beam  energy
            PT = samplerData.GetColumn('PT') # this is defined as pt= deltaE/(p0*c)

            E=E0*(1+PT) #This is the energy with a spread
        
            #Calculate sums
            s_s    = _np.sum(s)
            x_s    = _np.sum(x)
            y_s    = _np.sum(y)
            xp_s   = _np.sum(xp)
            yp_s   = _np.sum(yp)
            E_s    = _np.sum(E)
            EE_s   = _np.sum(E*E)
            xx_s   = _np.sum(x*x)
            xxp_s  = _np.sum(x*xp)
            xpxp_s = _np.sum(xp*xp)
            xpE_s  = _np.sum(xp*E)
            xE_s   = _np.sum(x*E)
            yy_s   = _np.sum(y*y)
            yyp_s  = _np.sum(y*yp)
            ypyp_s = _np.sum(yp*yp)
            ypE_s  = _np.sum(yp*E)
            yE_s   = _np.sum(y*E)

            wgt   = len(x) #this is a valid for ptc output as weight is always 1

            #normalise
            s_s    /= wgt
            x_s    /= wgt
            y_s    /= wgt
            xp_s   /= wgt
            yp_s   /= wgt
            E_s    /= wgt
            EE_s   /= wgt
            xx_s   /= wgt
            xxp_s  /= wgt
            xpxp_s /= wgt
            xpE_s  /= wgt
            xE_s   /= wgt
            yy_s   /= wgt
            yyp_s  /= wgt
            ypyp_s /= wgt
            ypE_s  /= wgt
            yE_s   /= wgt
            
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

            #if there is no energy spread it is expected that the dispersion would evaluate to inf, hence ignore
            #'divide by 0' runtime warning
            with _np.errstate(divide='ignore'):
                disp_x  = (xE_s  - (x_s  * E_s)) / (EE_s - (E_s * E_s))
                disp_xp = (xpE_s - (xp_s * E_s)) / (EE_s - (E_s * E_s))
                disp_y  = (yE_s  - (y_s  * E_s)) / (EE_s - (E_s * E_s))
                disp_yp = (ypE_s - (yp_s * E_s)) / (EE_s - (E_s * E_s))

            #### error calculations to be added

            sampler.append(isampler)
            S.append(s_s)            
            betx.append(beta_x)
            bety.append(beta_y)
            alphx.append(alph_x)
            alphy.append(alph_y)
            dispx.append(disp_x)
            dispy.append(disp_y)
            dispxp.append(disp_xp)
            dispyp.append(disp_yp)
            emittx.append(emitt_x)
            emitty.append(emitt_y)
            sigmax.append(sigma_x)
            sigmay.append(sigma_y)
            sigmaxp.append(sigma_xp)
            sigmayp.append(sigma_yp)
            sigmaxxp.append(sigma_x_xp)
            sigmayyp.append(sigma_y_yp)
            meanx.append(x_m)
            meany.append(y_m)
            meanxp.append(xp_m)
            meanyp.append(yp_m)
            Wgt.append(wgt)

        #prepare header    
        header = ['Segment','S[m]','Beta_x[m]','Beta_y[m]','Alph_x','Aplh_y']
        header.extend(['Disp_x','Disp_xp','Disp_y','Disp_yp'])
        header.extend(['Emitt_x','Emitt_y'])
        header.extend(['Sigma_x[m]','Sigma_y[m]','Sigma_xp[rad]','Sigma_yp[rad]'])
        header.extend(['Sigma_x_xp[m*rad]','Sigma_y_yp[m*rad]'])
        header.extend(['Mean_x[m]','Mean_y[m]','Mean_xp[rad]','Mean_yp[rad]','Wgt'])

        #prepare optical function arrays for writing to file

        for i in range(len(S)):
            S[i]=float("{0:.4e}".format(S[i]))
            betx[i]=float("{0:.4e}".format(betx[i]))
            bety[i]=float("{0:.4e}".format(bety[i]))
            alphx[i]=float("{0:.4e}".format(alphx[i]))
            alphy[i]=float("{0:.4e}".format(alphy[i]))
            dispx[i]=float("{0:.4e}".format(dispx[i]))
            dispy[i]=float("{0:.4e}".format(dispy[i]))
            dispxp[i]=float("{0:.4e}".format(dispxp[i]))
            dispyp[i]=float("{0:.4e}".format(dispyp[i]))
            emittx[i]=float("{0:.4e}".format(emittx[i]))
            emitty[i]=float("{0:.4e}".format(emitty[i]))
            sigmax[i]=float("{0:.4e}".format(sigmax[i]))
            sigmay[i]=float("{0:.4e}".format(sigmay[i]))
            sigmaxp[i]=float("{0:.4e}".format(sigmaxp[i]))
            sigmayp[i]=float("{0:.4e}".format(sigmayp[i]))
            sigmaxxp[i]=float("{0:.4e}".format(sigmaxxp[i]))
            sigmayyp[i]=float("{0:.4e}".format(sigmayyp[i]))
            meanx[i]=float("{0:.4e}".format(meanx[i]))
            meany[i]=float("{0:.4e}".format(meany[i]))
            meanxp[i]=float("{0:.4e}".format(meanxp[i]))
            meanyp[i]=float("{0:.4e}".format(meanyp[i]))
            Wgt[i]=float("{0:.4e}".format(Wgt[i]))

        with open(output,'w') as ofile:        
            writer=csv.writer(ofile, delimiter='\t',lineterminator='\n',)
            timestamp = time.strftime("%Y/%m/%d-%H:%M:%S")
            writer.writerow(['# ','Optical functions from PTC output', timestamp])
            writer.writerow(header)
            for i in range(len(S)):
                row = [sampler[i],S[i],betx[i],bety[i],alphx[i],alphy[i],dispx[i],dispy[i]]
                row.extend([dispxp[i],dispyp[i],emittx[i],emitty[i]])
                row.extend([sigmax[i],sigmay[i],sigmaxp[i],sigmayp[i],sigmaxxp[i],sigmayyp[i]])
                row.extend([meanx[i],meany[i],meanxp[i],meanyp[i],Wgt[i]])
                writer.writerow(row)

            
        
