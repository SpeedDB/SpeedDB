import argparse
import os.path

from speeddb.utils.mkdb import makeDB

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

v = get_version('__init__.py')

parser = argparse.ArgumentParser('SpeedDB', 'speeddb <command> [options]', )
parser.add_argument('-v', '--version', action='version', version=f'SpeedDB {v}', help='Show version')
parser.add_argument('-q', '--quite', action='store_true', help='Show less output')

command = parser.add_subparsers(title='commands', metavar='Commands List:', dest='command') # dest: stores command={command} in the args

build = command.add_parser('build', help='Create a new database', usage='speeddb build [options] <name>')
build.add_argument('name', type=str, help='Database name')

def runner():
   main(parser.parse_args())

def main(args:argparse.Namespace=None):
   if args.command == 'build':
      result = makeDB(args.name)

      if result.startswith('Error'):
         parser.exit(message=result)

if __name__ == '__main__':
   runner()