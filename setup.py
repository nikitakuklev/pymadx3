from setuptools import setup, find_packages

setup(
    name='pymadx',
    version='0.9.0',
    packages=find_packages(exclude=["docs", "tests", "obsolete"]),
    # Not sure how strict these need to be...
    install_requires=["matplotlib >= 1.7.1",
                      "numpy >= 1.3.0"],
    # Some version of python2.7
    python_requires="==2.7.*",

    author='JAI@RHUL',
    author_email='laurie.nevay@rhul.ac.uk',
    description="Write MADX models and load MADX output.",
    url='https://bitbucket.org/jairhul/pymadx/',
    license='GPL3',
    keywords='madx accelerator twiss ptc'
)
