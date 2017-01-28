from setuptools import setup

setup(
   name='pymadx',
   version='1.0',
   description='BDSIM python helper package',
   author='JAI@RHUL',
   author_email='stewart.boogert@rhul.ac.uk',
#   py_modules = ['__init__','Beam','Builder','Constants','Data','Gmad','Joinhistograms',
#                 'ModelProcessing','Options','Plot','Run','Visualisation','XSecBias','_General'],
   package_dir = {'pymadx': './'},
   packages=['pymadx'],
)
