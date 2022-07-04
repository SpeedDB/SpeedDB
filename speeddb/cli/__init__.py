import argparse
import os

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

# v = get_version('__init__.py')

parser = argparse.ArgumentParser('SpeedDB', 'speeddb <command> [options]', )

def runner():
   main(parser.parse_args())

def main(args:list[str]=None):
   print(args)