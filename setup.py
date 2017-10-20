from setuptools import setup, find_packages

setup(
    name='pymadx',
    version='0.9',
    packages=find_packages(exclude=["docs", "tests", "obsolete"]),
    # Not sure how strict these need to be...
    install_requires=["matplotlib >= 2.1.0",
                      "numpy >= 1.13"],
    # Some version of python2.7
    python_requires="==2.7.*",

    author='JAI@RHUL',
    author_email='stewart.boogert@rhul.ac.uk',
    description="Write MADX models and load MADX output.",
    url='https://bitbucket.org/jairhul/pymadx/'
)
