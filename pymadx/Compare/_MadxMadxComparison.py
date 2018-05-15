"""
Functions for comparing the optical distributions of two
BDSIM models.

Functions for plotting the individual optical functions, and an
eighth, helper function ''compare_all_optics``, to plot display all
seven in one go.
"""
import datetime as _datetime
import matplotlib.pyplot as _plt
from matplotlib.backends.backend_pdf import PdfPages as _PdfPages
import os.path as _path

import pymadx.Data as _Data
import pymadx.Plot as _Plot

# Predefined lists of tuples for making the standard plots,
# format = (optical_var_name, optical_var_error_name, legend_name)

_BETA = [("BETX", r'$\beta_{x}$'),
         ("BETY", r'$\beta_{y}$')]

_ALPHA = [("ALFX", r"$\alpha_{x}$"),
          ("ALFY", r"$\alpha_{y}$")]

_DISP = [("DXBETA", r"$D_{x}$ / $\beta$"),
         ("DYBETA", r"$D_{y}$ / $\beta$")]

_DISP_P = [("DPXBETA", r"$D_{p_{x}}$"),
           ("DPYBETA", r"$D_{p_{y}}$")]

_SIGMA = [("SIGMAX", r"$\sigma_{x}$"),
          ("SIGMAY", r"$\sigma_{y}$")]

_SIGMA_P = [("SIGMAXP", r"$\sigma_{xp}$"),
            ("SIGMAYP", r"$\sigma_{yp}$")]

_MEAN = [("X", r"$\bar{x}$"),
         ("Y", r"$\bar{y}$")]


def _parse_tfs_input(tfs_in, name):
    """Return tfs_in as a Tfs instance, which should either be a path
    to a TFS file or a Tfs instance, and in either case, generate a
    name if None is provided, and return that as well."""
    if isinstance(tfs_in, basestring):
        if not _path.isfile(tfs_in):
            raise IOError("file \"{}\" not found!".format(tfs_in))
        name = (_path.splitext(_path.basename(tfs_in))[0]
                if name is None else name)
        return _Data.Tfs(tfs_in), name
    try:
        name = tfs_in.filename if name is None else name
        return tfs_in, name
    except AttributeError:
        raise TypeError(
            "Expected Tfs input is neither a "
            "file path nor a Tfs instance: {}".format(tfs_in))


# use closure to avoid tonnes of boilerplate code as happened with
# MadxBdsimComparison.py
def _make_plotter(plot_info_tuples, x_label, y_label, title):
    def f_out(first, second, first_name=None, second_name=None, **kwargs):
        """first and second should be tfs files."""
        first, first_name = _parse_tfs_input(first, first_name)
        second, second_name = _parse_tfs_input(second, second_name)

        plot = _plt.figure(title, figsize=(9,5), **kwargs)
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


def MADXVsMADX(first, second, first_name=None,
               second_name=None, saveAll=True, 
               outputFileName=None, **kwargs):
    """
    Display all the optical function plots for the two input optics files.
    """
    figures = [
    PlotBeta(first, second, first_name=first_name,
             second_name=second_name, **kwargs),
    PlotAlpha(first, second, first_name=first_name,
              second_name=second_name, **kwargs),
    PlotDisp(first, second, first_name=first_name,
             second_name=second_name, **kwargs),
    PlotDispP(first, second, first_name=first_name,
              second_name=second_name, **kwargs),
    PlotSigma(first, second, first_name=first_name,
              second_name=second_name, **kwargs),
    PlotSigmaP(first, second, first_name=first_name,
               second_name=second_name, **kwargs),
    PlotMean(first, second, first_name=first_name,
             second_name=second_name, **kwargs),
    ]

    if saveAll:
        if outputFileName is not None:
            output_filename = outputFileName
        else:
            output_filename = "optics-report.pdf"

        with _PdfPages(output_filename) as pdf:
            for figure in figures:
                pdf.savefig(figure)
            d = pdf.infodict()
            d['Title'] = "{} VS {} Optical Comparison".format(first_name, second_name)
            d['CreationDate'] = _datetime.datetime.today()
        print "Written ", output_filename
