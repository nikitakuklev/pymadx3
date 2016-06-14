"""
Ploting script for madx TFS files using the pymadx Tfs class

"""

#need TFS but protect against already being imported in pymadx.__init__
#and therefore is a class and no longer a module - a consequence of
#the class having the same name as a file
try:
    from . import Tfs as _Tfs
except ImportError:
    import Tfs as _Tfs

from _General import CheckItsTfs as _CheckItsTfs

import numpy as _np
#protect against matplotlib import errors
try:
    import matplotlib         as _matplotlib
    import matplotlib.patches as _patches
    import matplotlib.pyplot  as _plt
except ImportError:
    print "pymadx.Plot -> WARNING - plotting will not work on this machine"
    print "matplotlib.pyplot doesn't exist"
    
class _My_Axes(_matplotlib.axes.Axes):
    """
    Inherit matplotlib.axes.Axes but override pan action for mouse.
    Only allow horizontal panning - useful for lattice axes.
    """
    name = "_My_Axes"
    def drag_pan(self, button, key, x, y):
        _matplotlib.axes.Axes.drag_pan(self, button, 'x', x, y) # pretend key=='x'

#register the new class of axes
_matplotlib.projections.register_projection(_My_Axes)

def _GetOpticalDataFromTfs(tfsobject):
    d = {}
    d['s']     = tfsobject.GetColumn('S')
    d['betx']  = tfsobject.GetColumn('BETX')
    d['bety']  = tfsobject.GetColumn('BETY')
    d['dispx'] = tfsobject.GetColumn('DX')
    d['dispy'] = tfsobject.GetColumn('DY')
    d['x']     = tfsobject.GetColumn('X')
    d['y']     = tfsobject.GetColumn('Y')
    return d

def PlotTfsBetaSimple(tfsfile, title='', outputfilename=None):
    """
    Plot the sqrt(beta x,y) as a function of S
    """
    madx = _CheckItsTfs(tfsfile)
    d    = _GetOpticalDataFromTfs(madx)

    _plt.figure()
    _plt.plot(d['s'],_np.sqrt(d['betx']),'b-', label=r'$\sqrt{\beta_{x}}$')
    _plt.plot(d['s'],_np.sqrt(d['bety']),'g-', label=r'$\sqrt{\beta_{y}}$')
    _plt.xlabel(r'$\mathrm{S (m)}$')
    _plt.ylabel(r'$\sqrt{\beta_{x,y}}$ $\sqrt{\mathrm{m}}$')
    _plt.legend(loc=0) #best position
    _plt.title(title)

    if outputfilename != None:
        if '.' in outputfilename:
            outputfilename = outputfilename.split('.')[0]
        _plt.savefig(outputfilename+'.pdf')
        _plt.savefig(outputfilename+'.png')

def PlotTfsBeta(tfsfile, title='',outputfilename=None, dispersion=False):
    """
    Plot sqrt(beta x,y) as a function of S as well as the horizontal dispersion.

    Also adds machine lattice at the top of the plot
    """
    madx = _CheckItsTfs(tfsfile)
    d    = _GetOpticalDataFromTfs(madx)
    smax = madx.smax

    f    = _plt.figure(figsize=(11,5))
    axoptics = f.add_subplot(111)

    #optics plots
    axoptics.plot(d['s'],_np.sqrt(d['betx']),'b-', label=r'$\sqrt{\beta_{x}}$')
    axoptics.plot(d['s'],_np.sqrt(d['bety']),'g-', label=r'$\sqrt{\beta_{y}}$')
    if dispersion:
        axoptics.plot(-100,-100,'r--', label=r'$\mathrm{D}(x)$') #fake plot for legend
    axoptics.set_xlabel('S (m)')
    axoptics.set_ylabel(r'$\sqrt{\beta_{x,y}}$ ($\sqrt{\mathrm{m}}$)')
    axoptics.legend(loc=0,fontsize='small') #best position

    #plot dispersion - only in horizontal
    if dispersion:
        ax2 = axoptics.twinx()
        ax2.plot(d['s'],d['dispx'],'r--')
        ax2.set_ylabel('Dispersion (m)')

    #add lattice to plot
    AddMachineLatticeToFigure(f,madx)

    _plt.suptitle(title,size='x-large')
    
    if outputfilename != None:
        if '.' in outputfilename:
            outputfilename = outputfilename.split('.')[0]
        _plt.savefig(outputfilename+'.pdf')
        _plt.savefig(outputfilename+'.png')

def AddMachineLatticeToFigure(figure,tfsfile):
    tfs = _CheckItsTfs(tfsfile) #load the machine description

    axs = figure.get_axes() # get the existing graph
    axoptics = axs[0]       # get the only presumed axes from the figure
    
    #adjust existing plot to make way for machine lattice
    #iterate over axes incase there's dual plots
    nAxesNewX = len(axs) + 1 # there will be one more new axis
    ratios = [5]*len(axs) # here we assume if there are other figures, they're equal proportion
    ratios.insert(0,1) # put the small one at the front, 1/5 the size of the others
    gs = _plt.GridSpec(nAxesNewX,1,height_ratios=tuple(ratios))
    # apparently, gridspec is like a list but doesn't implement len or shape
    # and it's in reverse order compared to the axes from a figure - it's bad
    for i,ax in enumerate(axs):
        gsindex = i+1
        ax.set_position(gs[gsindex].get_position(figure))
        ax.set_subplotspec(gs[gsindex])

    #add new axes for machine lattice
    axmachine = figure.add_subplot(gs[0], projection="_My_Axes")
    axmachine.get_xaxis().set_visible(False)
    axmachine.get_yaxis().set_visible(False)
    axmachine.spines['top'].set_visible(False)
    axmachine.spines['bottom'].set_visible(False)
    axmachine.spines['left'].set_visible(False)
    axmachine.spines['right'].set_visible(False)
    figure.set_facecolor('white')
    # leave plot as it was
    #_plt.subplots_adjust(hspace=0.01,top=0.94,left=0.1,right=0.92,wspace=originalwspace)

    #generate the machine lattice plot
    _DrawMachineLattice(axmachine,tfs)
    xl = axmachine.get_xlim()
    xr = xl[1] - xl[0]
    axoptics.set_xlim(xl[0]-0.02*xr,xl[1]+0.02*xr)
    axmachine.set_xlim(xl[0]-0.02*xr,xl[1]+0.02*xr)

    #put callbacks for linked scrolling
    def MachineXlim(ax): 
        axmachine.set_autoscale_on(False)
        for ax in axs:
            ax.set_xlim(axmachine.get_xlim())
            #axoptics.set_xlim(axmachine.get_xlim())

    def Click(a) : 
        if a.button == 3 : 
            print 'Closest element: ',tfs.NameFromNearestS(a.xdata)

    axmachine.callbacks.connect('xlim_changed', MachineXlim)
    figure.canvas.mpl_connect('button_press_event', Click) 

def _DrawMachineLattice(axesinstance,pymadxtfsobject):
    ax  = axesinstance #handy shortcut
    tfs = pymadxtfsobject

    #NOTE madx defines S as the end of the element by default
    #define temporary functions to draw individual objects
    def DrawBend(e,color='b',alpha=1.0):
        br = _patches.Rectangle((e['S']-e['L'],-0.1),e['L'],0.2,color=color,alpha=alpha)
        ax.add_patch(br)
    def DrawQuad(e,color='r',alpha=1.0):
        if e['K1L'] > 0 :
            qr = _patches.Rectangle((e['S']-e['L'],0),e['L'],0.2,color=color,alpha=alpha)
        elif e['K1L'] < 0: 
            qr = _patches.Rectangle((e['S']-e['L'],-0.2),e['L'],0.2,color=color,alpha=alpha)
        else:
            #quadrupole off
            qr = _patches.Rectangle((e['S']-e['L'],-0.1),e['L'],0.2,color='#B2B2B2',alpha=0.5) #a nice grey in hex
        ax.add_patch(qr)
    def DrawHex(e,color,alpha=1.0):
        s = e['S']-e['L']
        l = e['L']
        edges = _np.array([[s,-0.1],[s,0.1],[s+l/2.,0.13],[s+l,0.1],[s+l,-0.1],[s+l/2.,-0.13]])
        sr = _patches.Polygon(edges,color=color,fill=True,alpha=alpha)
        ax.add_patch(sr)
    def DrawRect(e,color,alpha=1.0):
        rect = _patches.Rectangle((e['S']-e['L'],-0.1),e['L'],0.2,color=color,alpha=alpha)
        ax.add_patch(rect)
    def DrawLine(e,color,alpha=1.0):
        ax.plot([e['S']-e['L'],e['S']-e['L']],[-0.2,0.2],'-',color=color,alpha=alpha)
            
    # plot beam line 
    ax.plot([0,tfs.smax],[0,0],'k-',lw=1)
    ax.set_ylim(-0.5,0.5)
 
    # loop over elements and Draw on beamline
    for element in tfs:
        kw = element['KEYWORD']
        if kw == 'QUADRUPOLE': 
            DrawQuad(element)
        elif kw == 'RBEND': 
            DrawBend(element)
        elif kw == 'SBEND': 
            DrawBend(element)
        elif kw == 'RCOLLIMATOR': 
            DrawRect(element,'k')
        elif kw == 'ECOLLIMATOR': 
            DrawRect(element,'k')
        elif kw == 'SEXTUPOLE':
            DrawHex(element,'#ffcf17') #yellow
        elif kw == 'OCTUPOLE':
            DrawHex(element,'g')
        elif kw == 'DRIFT':
            pass
        elif kw == 'MULTIPOLE':
            DrawHex(element,'grey',alpha=0.5)
        else:
            #unknown so make light in alpha
            if element['L'] > 1e-1:
                DrawRect(element,'#cccccc',alpha=0.1) #light grey
            else:
                #relatively short element - just draw a line
                DrawLine(element,'#cccccc',alpha=0.1)
