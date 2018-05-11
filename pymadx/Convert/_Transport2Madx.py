# Wrapper for pytransport conversion.

from pymadx import Builder as _mdBuilder


from pytransport.Convert import _Convert
from pytransport.Data import ConversionData


def Transport2Madx(inputfile,
                   particle='proton',
                   distrType='gauss',
                   outputDir='madx',
                   debug=False,
                   dontSplit=False,
                   keepName=False,
                   combineDrifts=False):
    """
    **Transport2Madx** convert a Transport input or output file into a madx input file for madx

    +-------------------------------+-------------------------------------------------------------------+
    | **inputfile**                 | dtype = string                                                    |
    |                               | path to the input file                                            |
    +-------------------------------+-------------------------------------------------------------------+
    | **particle**                  | dtype = string. Optional, default = "proton"                      |
    |                               | the particle species                                              |
    +-------------------------------+-------------------------------------------------------------------+
    | **distrType**                 | dtype = string. Optional, Default = "gauss".                      |
    |                               | the beam distribution type. Can be either gauss or gausstwiss.    |
    +-------------------------------+-------------------------------------------------------------------+
    | **outputDir**                 | dtype=string. Optional, default = "gmad"                          |
    |                               | the output directory where the files will be written              |
    +-------------------------------+-------------------------------------------------------------------+
    | **debug**                     | dtype = bool. Optional, default = False                           |
    |                               | output a log file (inputfile_conversion.log) detailing the        |
    |                               | conversion process, element by element                            |
    +-------------------------------+-------------------------------------------------------------------+
    | **dontSplit**                 | dtype = bool. Optional, default = False                           |
    |                               | the converter splits the machine into multiple parts when a beam  |
    |                               | is redefined in a Transport lattice. dontSplit overrides this and |
    |                               | forces the machine to be written to a single file                 |
    +-------------------------------+-------------------------------------------------------------------+
    | **keepName**                  | dtype = bool. Optional, default = False                           |
    |                               | keep the names of elements as defined in the Transport inputfile. |
    |                               | Appends element name with _N where N is an integer if the element |
    |                               | name has already been used                                        |
    +-------------------------------+-------------------------------------------------------------------+
    | **combineDrifts**             | dtype = bool. Optional, default = False                           |
    |                               | combine multiple consecutive drifts into a single drift           |
    +-------------------------------+-------------------------------------------------------------------+

    Example:

    >>> Transport2Madx(inputfile)

    Writes converted machine to disk. Reader automatically detects if the supplied input file is a Transport input
    file or Transport output file.

    """
    converter = _Convert(ConversionData(inputfile=inputfile, options=None, machine=_mdBuilder.Machine(),
                                        particle=particle, debug=debug, distrType=distrType, gmad=False, gmadDir='',
                                        madx=True, madxDir=outputDir, dontSplit=dontSplit, keepName=keepName,
                                        combineDrifts=combineDrifts))
    # automatically convert
    converter.Convert()

