from setuptools import find_packages, setup
import os
import py2exe

def read(rel_path):
   import codecs
   here = os.path.abspath(os.path.dirname(__file__))
   with codecs.open(os.path.join(here, rel_path), 'r') as fp:
      return fp.read()

def get_version(rel_path):
   for line in read(rel_path).splitlines():
      if line.startswith('__version__'):
         delim = '"' if '"' in line else "'"
         return line.split(delim)[1]
   else:
      raise RuntimeError("Unable to find version string.")

# SpeedDB\SpeedDB\speeddb/__init__.py
v = get_version('speeddb/__init__.py')

setup(
   name='speeddb',
   packages=find_packages(),
   install_requires=[
      'pyonr>=2.0.0'
   ],
   include_package_data=True,
   version=v,
   author='Nawaf Alqari',
   author_email='nawafalqari13@gmail.com',
   keywords=['speeddb', 'db', 'fast', 'speed'],
   long_description='soon..',
   entry_points={
      'console_scripts': ['speeddb=speeddb.cli:runner']
   },
   # console=['speeddb/cli.py'],
   license='MIT',
   zip_safe=False,
   url='https://github.com/SpeedDB/SpeedDB',
   project_urls={
      'Documentation': 'https://github.com/SpeedDB/SpeedDB#readme',
      'Bug Tracker': 'https://github.com/SpeedDB/SpeedDB/issues',
      'Source Code': 'https://github.com/SpeedDB/SpeedDB',
      'Discord': 'https://discord.gg/cpvynqk4XT',
      'Donate': 'https://paypal.me/NawafHAlqari'
    },
    classifiers=[
      'Programming Language :: Python :: 3',
      'License :: OSI Approved :: MIT License',
      'Operating System :: OS Independent',
      'Topic :: Database'
    ]
)