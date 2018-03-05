"""
Functions for comparing the optical distributions of two
BDSIM models.

Functions for plotting the individual optical functions, and an
eighth, helper function ''compare_all_optics``, to plot display all
seven in one go.
"""

import os.path as _path
import matplotlib.pyplot as _plt

import pymadx.Data as _Data
import pymadx.Plot as _Plot

# Predefined lists of tuples for making the standard plots,
# format = (optical_var_name, optical_var_error_name, legend_name)

_BETA = [("BETX", r'$\beta_{x}$'),
         ("BETY", r'$\beta_{y}$')]

_ALPHA = [("ALFX", r"$\alpha_{x}$"),
          ("ALFY", r"$\alpha_{y}$")]

_DISP = [("DX", r"$D_{x}$"),
         ("DY", r"$D_{y}$")]

_DISP_P = [("DPX", r"$D_{p_{x}}$"),
           ("DPY", r"$D_{p_{y}}$")]

_SIGMA = [("SIGMAX", r"$\sigma_{x}$"),
          ("SIGMAY", r"$\sigma_{y}$")]

_SIGMA_P = [("SIGMAXP", r"$\sigma_{xp}$"),
            ("SIGMAYP", r"$\sigma_{yp}$")]

_MEAN = [("X", r"$\bar{x}$"),
         ("Y", r"$\bar{y}$")]

# use closure to avoid tonnes of boilerplate code as happened with
# MadxBdsimComparison.py
def _make_plotter(plot_info_tuples, x_label, y_label, title):
    def f_out(first, second, first_name=None, second_name=None, **kwargs):
        """first and second should be tfs files."""
        if not _path.isfile(first):
            raise IOError("file \"{}\" not found!".format(first))
        if not _path.isfile(second):
            raise IOError("file \"{}\" not found!".format(second))

        # If no names provided then just use the filenames.
        first_name = (_path.splitext(_path.basename(first))[0]
                      if first_name is None else first_name)
        second_name = (_path.splitext(_path.basename(second))[0]
                       if second_name is None else second_name)

        first  = _Data.Tfs(first)
        second = _Data.Tfs(second)

        plot = _plt.figure(title, **kwargs)
        # Loop over the variables in plot_info_tuples and draw the plots.
        for var, legend_name in plot_info_tuples:
            _plt.plot(first.GetColumn('S'), first.GetColumn(var),
                      label="{}: {}".format(legend_name, first_name), **kwargs)
            _plt.plot(second.GetColumn('S'), second.GetColumn(var),
                      label="{}: {}".format(legend_name, second_name), **kwargs)

        # Set axis labels and draw legend
        axes = _plt.gcf().gca()
        axes.set_ylabel(y_label)
        axes.set_xlabel(x_label)
        axes.legend(loc='best')

        _Plot.AddMachineLatticeToFigure(plot, first)
        _plt.show(block=False)
        return plot
    return f_out

PlotBeta   = _make_plotter(_BETA,    "S / m", r"$\beta_{x,y}$ / m",      "Beta")
PlotAlpha  = _make_plotter(_ALPHA,   "S / m", r"$\alpha_{x,y}$ / m",     "Alpha")
PlotDisp   = _make_plotter(_DISP,    "S / m", r"$D_{x,y} / m$",          "Dispersion")
PlotDispP  = _make_plotter(_DISP_P,  "S / m", r"$D_{p_{x},p_{y}}$ / m",  "Momentum_Dispersion")
PlotSigma  = _make_plotter(_SIGMA,   "S / m", r"$\sigma_{x,y}$ / m",     "Sigma")
PlotSigmaP = _make_plotter(_SIGMA_P, "S / m", r"$\sigma_{xp,yp}$ / rad", "SigmaP")
PlotMean   = _make_plotter(_MEAN,    "S / m", r"$\bar{x}, \bar{y}$ / m", "Mean")


def MADXvsMADX(first, second, first_name=None,
               second_name=None, **kwargs):
    """
    Display all the optical function plots for the two input optics files.
    """
    PlotBeta(first, second, first_name=first_name,
             second_name=second_name, **kwargs)
    PlotAlpha(first, second, first_name=first_name,
              second_name=second_name, **kwargs)
    PlotDisp(first, second, first_name=first_name,
             second_name=second_name, **kwargs)
    PlotDispP(first, second, first_name=first_name,
              second_name=second_name, **kwargs)
    PlotSigma(first, second, first_name=first_name,
              second_name=second_name, **kwargs)
    PlotSigmaP(first, second, first_name=first_name,
               second_name=second_name, **kwargs)
    PlotMean(first, second, first_name=first_name,
             second_name=second_name, **kwargs)
