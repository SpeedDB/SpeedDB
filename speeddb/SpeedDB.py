from pyonr import read
from pyonr.converter import convert, PYON, OBJ
from uvicorn import run as runServer
from uvicorn import Config, Server
from threading import Thread
from socket import gethostbyname, gethostname
from os.path import abspath
from requests import request as _req
from typing import Dict
from os.path import isfile

from speeddb.utils.mkdb import schema
from speeddb.utils.server import makeServer
from .errors import *
from multiprocessing import freeze_support

class SpeedDBServer:
   """
   
   `SpeedDBServer` is used to run a server to get/send data using `SpeedDBClient`

   """
   def __init__(self, dbsPath:str='.', local:bool=True, port:int=5440):
      """
      
      Parameters:
      -----------

      `dbsPath` : str
         Where your databases are stored (1 or more databases), "." is referred to the file path
         
      `local` : bool
         If `False` the server will run on your IP Address which means you can access it from any device on the same network,
         If `True` the server will only be accessible on your machine, default=True

      `port` : int
         The port that the server will run on, default=5440
      
      """
      
      self.dbsPath = abspath(dbsPath)
      self.local = local
      self.port = port
      self.server = makeServer(self.dbsPath)

   def _runServer(self, workers:int):
      config = Config(self.server, port=self.port, log_level='error', workers=workers)
      if not self.local:
         config.host = '0.0.0.0'
         server = Server(config)
         server.run()
         # runServer(self.server, host='0.0.0.0', port=self.port, log_level='error', workers=workers)
      else:
         server = Server(config)
         server.run()
         # runServer('self.server', port=self.port, log_level='error', workers=workers)

   def _buildURL(self):
      url = 'http://'

      if self.local:
         url += '127.0.0.1'
      else:
         url += gethostbyname(gethostname()) # IPv4 Address
         
      url += f':{self.port}'

      return url

   def run(self, daemon:bool=False, workers:int=3):


      if not daemon:
         print(f'SpeedDB Server is running on {self._buildURL()}')
         self._runServer(workers)

         return self._buildURL()
      else:
         print(f'SpeedDB Server is running on {self._buildURL()}')
         thread = Thread(target=self._runServer, daemon=True, name='SpeedDB Server', kwargs={'workers': workers})

         self.thread = thread
         
         thread.start()

         return self._buildURL()
         
   def shutdown(self):
      self.thread
         
class SpeedDBDatabase:
   def __init__(self, dbHost:str, dbName:str=None, hostType:str=None):
      if isfile(dbHost):
         self.hostType = 'file'
         self.r = read(dbHost)
      else:
         self.hostType = hostType

      self.dbHost = dbHost
      self.dbName = dbName

   def _HttpRead(self):
      return convert(PYON, OBJ, _req('GET', self.dbHost).content.decode('utf-8'))

   def _HttpWrite(self, documents:dict):
      req = _req('POST', self.dbHost, data={
         'data': f'{convert(OBJ, PYON, documents)}'
      })

      return req.json()

   def _FileRead(self):
      return self.r.read

   def _FileWrite(self, documents:dict):
      self.r.write(documents)
      
   def get(self, _filter:dict) -> dict:
      if not isinstance(_filter, dict):
         raise TypeError(f'Unexpected _filter type: {_filter.__class__.__name__}')

      document = self.getMany(_filter)
      return None if not document else document[0]

   def getMany(self, _filter:dict) -> list:
      if not isinstance(_filter, dict):
         raise TypeError(f'Unexpected _filter type: {_filter.__class__.__name__}')

      if self.hostType == 'http':
         documents = algorithm(self._HttpRead()['__docs'], _filter)
         return None if not documents else documents 

      if self.hostType == 'file':
         documents = algorithm(self._FileRead()['__docs'], _filter)

         return None if not documents else documents

   def append(self, document:dict):
      '''
      `Append One` document to the database

      >>> name = input('What is your name: ')
      >>> db.append({'name': name})
      
      '''
      if not isinstance(document, dict):
         raise TypeError(f'Unexpected document type of: {document.__class__.__name__}')

      if self.hostType == 'http':
         dbData = self._HttpRead()

         dbData['__docs'].append(document)
         self._HttpWrite(dbData)

      if self.hostType == 'file':
         dbData = self._FileRead()

         dbData['__docs'].append(document)
         self._FileWrite(dbData)

   def appendMany(self, documents:list[dict]):
      '''
      `Append Many` documents to the database

      >>> names = [input('name: ') for name in range(3)] # will show 3 inputs
      >>> db.appendMany(names)
      
      '''

      if not isinstance(documents, list):
         raise TypeError(f'Unexpected documents type: {documents.__class__.__name__}')
      if not allTypes(documents, dict):
         raise TypeError(f'Documents elements must be dict')

      for document in documents:
         self.append(document)

   def remove(self, _filter:dict):
      if not isinstance(_filter, dict):
         raise TypeError(f'Unexpected _filter type: {_filter.__class__.__name__}')
      
      if self.hostType == 'http':
         dbData = self._HttpRead()
         fullDocument = self.get(_filter)

         dbData['__docs'].remove(fullDocument)
         self._HttpWrite(dbData)

      if self.hostType == 'file':
         dbData = self._FileRead()
         fullDocument = self.get(_filter)

         dbData['__docs'].remove(fullDocument)
         self._FileWrite(dbData)

   def removeMany(self, _filter:dict):
      if not isinstance(_filter, dict):
         raise TypeError(f'Unexpected _filter type: {_filter.__class__.__name__}')
      
      if _filter == {}:
         if self.hostType == 'http':
            self._HttpWrite(schema)
         if self.hostType == 'file':
            self._FileWrite(schema)

      else:
         documents = self.getMany(_filter)

         for document in documents:
            self.remove(document)

   def update(self, _filter:dict, update:dict):
      if not isinstance(_filter, dict):
         raise TypeError(f'Unexpected _filter type: {_filter.__class__.__name__}')
      if not isinstance(update, dict):
         raise TypeError(f'Unexpected update type: {update.__class__.__name__}')

      if self.hostType == 'http':
         dbData = self._HttpRead()
         fullDocument = self.get(_filter)
         documentIndex = dbData['__docs'].index(fullDocument)

         dbData['__docs'][documentIndex] = update

         self._HttpWrite(dbData)

      if self.hostType == 'file':
         dbData = self._FileRead()
         fullDocument = self.get(_filter)
         documentIndex = dbData['__docs'].index(fullDocument)

         dbData['__docs'][documentIndex] = update

         self._FileWrite(dbData)
   
class SpeedDBClient:
   def __init__(self, host:str=None):
      if host is None:
         try:
            defaultHost = 'http://localhost:5440' 
            _req('HEAD', defaultHost)

            self.host = defaultHost
            self.__hostType = 'http'
         except:
            raise ConnectionError("Couldn't connect to default host, did you forget to specifiy the host?")

      else:
         try:
            _req('HEAD', host)

            self.host = host
            self.__hostType = 'http'
         except:
            raise ConnectionError(f"{host} is an invalid host")

      if self.hostType == 'http':
         self.__dbs = _req('GET', self.host).json()['dbs']

   @property
   def hostType(self):
      return self.__hostType

   @property
   def databases(self) -> Dict[str, SpeedDBDatabase]:
      dbNames = map(lambda e:e.removesuffix('.sdb'), self.__dbs)
      dbs = {
         db: SpeedDBDatabase(self._buildDBURL(db), db, self.hostType) for db in dbNames
      }
      return dbs

   def _buildDBURL(self, dbName:str):
      tempDBName = None
      if not dbName.endswith('.sdb'):
         tempDBName = f'{dbName}.sdb'

      if (dbName not in self.__dbs) and (tempDBName not in self.__dbs):
         raise InvalidDBNameError(f'{dbName} is not in databases list')

      URLResult = ''

      if self.host.endswith('/'):
         URLResult += f'{self.host}{dbName}'
      else:
         URLResult += f'{self.host}/{dbName}'

      return URLResult

def algorithm(documents, _filter):
   return [d for d in documents if sum(1 for k, v in d.items() if _filter.get(k)==v) >= len(_filter)]

def allTypes(l:list, _type):
   '''
   Checks if every element in a list is the same `type`

   ```python
   >>> l = [1, 2, 3, 'str']
   >>> checkTypes(l, int)
   False
   ```
   '''
   return list(filter(lambda e:type(e) == _type, l)) == l