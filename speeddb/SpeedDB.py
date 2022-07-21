from pyonr import read
from pyonr.converter import convert, PYON, OBJ
from threading import Thread
from socket import gethostbyname, gethostname, socket, AF_INET, SOCK_DGRAM
from requests import request as _req
from typing import Dict, List
from os.path import isfile, split, join
from os import listdir

from speeddb.utils.database import schema
from speeddb.utils.server import RunUDPServer
from .errors import *

# class SpeedDBDatabase:
   # def __init__(self, dbHost:str, dbName:str=None, hostType:str=None):
   #    if isfile(dbHost):
   #       self.hostType = 'file'
   #       self.r = read(dbHost)
   #    else:
   #       self.hostType = hostType

   #    self.dbHost = dbHost
   #    self.dbName = dbName

   # def _HttpRead(self):
   #    return convert(PYON, OBJ, _req('GET', self.dbHost).content.decode('utf-8'))

   # def _HttpWrite(self, documents:dict):
   #    req = _req('POST', self.dbHost, data={
   #       'data': f'{convert(OBJ, PYON, documents)}'
   #    })

   #    return req.json()

   # def _FileRead(self):
   #    return self.r.read

   # def _FileWrite(self, documents:dict):
   #    self.r.write(documents)
      
   # def get(self, _filter:dict) -> dict:
   #    if not isinstance(_filter, dict):
   #       raise TypeError(f'Unexpected _filter type: {_filter.__class__.__name__}')

   #    document = self.getMany(_filter)
   #    return None if not document else document[0]

   # def getMany(self, _filter:dict) -> list:
   #    if not isinstance(_filter, dict):
   #       raise TypeError(f'Unexpected _filter type: {_filter.__class__.__name__}')

   #    if self.hostType == 'http':
   #       return algorithm(self._HttpRead()['__docs'], _filter)

   #    if self.hostType == 'file':
   #       return algorithm(self._FileRead()['__docs'], _filter)

   # def append(self, document:dict):
   #    '''
   #    `Append One` document to the database

   #    >>> name = input('What is your name: ')
   #    >>> db.append({'name': name})
      
   #    '''
   #    if not isinstance(document, dict):
   #       raise TypeError(f'Unexpected document type of: {document.__class__.__name__}')

   #    if self.hostType == 'http':
   #       dbData = self._HttpRead()

   #       dbData['__docs'].append(document)
   #       self._HttpWrite(dbData)

   #    if self.hostType == 'file':
   #       dbData = self._FileRead()

   #       dbData['__docs'].append(document)
   #       self._FileWrite(dbData)

   # def appendMany(self, documents):
   #    '''
   #    `Append Many` documents to the database

   #    >>> names = [input('name: ') for name in range(3)] # will show 3 inputs
   #    >>> db.appendMany(names)
      
   #    '''

   #    if not isinstance(documents, list):
   #       raise TypeError(f'Unexpected documents type: {documents.__class__.__name__}')
   #    if not allTypes(documents, dict):
   #       raise TypeError(f'Documents elements must be dict')

   #    for document in documents:
   #       self.append(document)

   # def remove(self, _filter:dict):
   #    if not isinstance(_filter, dict):
   #       raise TypeError(f'Unexpected _filter type: {_filter.__class__.__name__}')
      
   #    if self.hostType == 'http':
   #       dbData = self._HttpRead()
   #       fullDocument = self.get(_filter)

   #       dbData['__docs'].remove(fullDocument)
   #       self._HttpWrite(dbData)

   #    if self.hostType == 'file':
   #       dbData = self._FileRead()
   #       fullDocument = self.get(_filter)

   #       dbData['__docs'].remove(fullDocument)
   #       self._FileWrite(dbData)

   # def removeMany(self, _filter:dict):
   #    if not isinstance(_filter, dict):
   #       raise TypeError(f'Unexpected _filter type: {_filter.__class__.__name__}')
      
   #    if _filter == {}:
   #       if self.hostType == 'http':
   #          self._HttpWrite(schema)
   #       if self.hostType == 'file':
   #          self._FileWrite(schema)

   #    else:
   #       documents = self.getMany(_filter)

   #       for document in documents:
   #          self.remove(document)

   # def update(self, _filter:dict, update:dict):
   #    if not isinstance(_filter, dict):
   #       raise TypeError(f'Unexpected _filter type: {_filter.__class__.__name__}')
   #    if not isinstance(update, dict):
   #       raise TypeError(f'Unexpected update type: {update.__class__.__name__}')

   #    if self.hostType == 'http':
   #       dbData = self._HttpRead()
   #       fullDocument = self.get(_filter)
   #       documentIndex = dbData['__docs'].index(fullDocument)

   #       dbData['__docs'][documentIndex] = update

   #       self._HttpWrite(dbData)

   #    if self.hostType == 'file':
   #       dbData = self._FileRead()
   #       fullDocument = self.get(_filter)
   #       documentIndex = dbData['__docs'].index(fullDocument)

   #       dbData['__docs'][documentIndex] = update

   #       self._FileWrite(dbData)
   
   

class SpeedDBServer:
   '''
   
   `SpeedDBServer` is used to run a udp server to send/receive database data

   '''
   def __init__(self, databasesPath:str, localServer:bool=True, port:int=5440):
      '''
      


      '''
      self.databasesPath = databasesPath
      self.localServer = localServer
      self.port = port

   def _buildIP(self):
      ip = ''
      ipAddr = ''
      port = self.port
      address = ()

      if self.localServer:
         ipAddr = '127.0.0.1'
         ip += ipAddr
      else:
         ipAddr = gethostbyname(gethostname()) # IPv4 Address
         ip += ipAddr
         
      ip += f':{self.port}'
      adress = (ipAddr, port)

      return ip, adress

   def run(self, daemon:bool=False):
      '''
      
      run the udp server

      Parameters:
      -----------
      
      `daemon`: bool = False
         Run the server as daemon (in the background)
      
      '''
      
      if not daemon:
         ip, address = self._buildIP()
         print(f'SpeedDB Server is running in {ip}, {address}')

         RunUDPServer(self.databasesPath, self.localServer, self.port)

         return ip, address

      else:
         ip, address = self._buildIP()
         print(f'SpeedDB Server is running in {ip}, {address}')
         
         serverThread = Thread(target=RunUDPServer, args=(self.databasesPath, self.localServer, self.port), daemon=daemon)
         serverThread.run()

         return ip, address

   def shutdown(self):
      # TODO: Make server shutdown when self.shutdown is called
      pass

   def stop(self):
      self.shutdown()

class UDPDatabase:
   def __init__(self, client:socket, address:tuple, dbName:str, bufferSize:int=1024):
      self.client = client
      self.dbName = dbName
      self.addr = address
      self.bufferSize = bufferSize

   def _buildData(self, **kwargs):
      return convert(OBJ, PYON, {**kwargs})

   def _send(self, data:str):
      dataLength = f'{len(data)}'.encode('utf-8')
      data = data.encode('utf-8')

      self.client.sendto(dataLength, self.addr)
      self.client.sendto(data, self.addr)

   def _recv(self):
      dataLength, address = self.client.recvfrom(self.bufferSize)

      if dataLength:
         data, address = self.client.recvfrom(int(dataLength))
         data = data.decode('utf-8')

         if data.startswith('Error: '):
            raise ServerError(data)

         else:
            data = convert(PYON, OBJ, data)

            return data

   @property
   def documents(self) -> int:
      return len(self.getMany({}))
      
   def get(self, _filter:dict):
      if not isinstance(_filter, dict):
         raise TypeError(f'_filter should be dictionary not {getClassName(_filter)}')

      documents = self.getMany(_filter)
      return None if not documents else documents[0]

   def getMany(self, _filter:dict):
      actionType = 'getMany'
      if not isinstance(_filter, dict):
         raise TypeError(f'_filter should be dictionary not {getClassName(_filter)}')

      self._send(self._buildData(
         type=actionType,
         dbName=self.dbName,
         data=_filter
      ))

      return self._recv()

   def append(self, document:dict):
      actionType = 'append'
      if not isinstance(document, dict):
         raise TypeError(f'document should be dictionary not {getClassName(document)}')

      self._send(self._buildData(
         type=actionType,
         dbName=self.dbName,
         data=document
      ))

   def appendMany(self, documents:List[Dict]):
      actionType = 'appendMany'
      if not isinstance(documents, list):
         raise TypeError(f'documents should be list not {getClassName(documents)}')
      if not allTypes(documents, dict):
         raise TypeError(f'every element in documents must be dictionary')

      self._send(self._buildData(
         type=actionType,
         dbName=self.dbName,
         data=documents
      ))

   def remove(self, _filter:dict):
      actionType = 'remove'
      if not isinstance(_filter, dict):
         raise TypeError(f'_filter should be dictionary not {getClassName(_filter)}')
      
      self._send(self._buildData(
         type=actionType,
         dbName=self.dbName,
         data=_filter
      ))

   def removeMany(self, _filter:dict):
      actionType = 'removeMany'
      if not isinstance(_filter, dict):
         raise TypeError(f'_filter should be dictionary not {getClassName(_filter)}')
      
      self._send(self._buildData(
         type=actionType,
         dbName=self.dbName,
         data=_filter
      ))

   def update(self, _filter:dict, update:dict):
      actionType = 'update'
      if not isinstance(_filter, dict):
         raise TypeError(f'_filter should be dictionary not {getClassName(_filter)}')

      if not isinstance(update, dict):
         raise TypeError(f'update should be dictionary not {getClassName(update)}')
      
      self._send(self._buildData(
         type=actionType,
         dbName=self.dbName,
         data=_filter,
         update=update
      ))

class SpeedDBClient:
   def __init__(self, address=None, *, ip=None, port=None, bufferSize:int=1024):
      '''
      
      `SpeedDBClient` is a client to send/receive data from multiple databases that are ran using `SpeedDBServer`
      
      Parameters:
      -----------

      `address`: tuple = None
         the server's address (ip, port)
         
         example: `('127.0.0.1', 5440)`

      `ip`: str = None
         the server's ip address (not required if the address was given)

      `port`: int = None
         the server's port (not required if the address was given)

      `bufferSize`: int = 1024
         buffer size which is used in `socket.recvfrom(bufferSize)`

      Important Note:

      if the `address` + `ip` + `port` were not given
         the default values for them will be:
            - `address=('127.0.0.1', 5440)`
            - `ip='127.0.0.1'`
            - `port=5440`

      You have to specifiy either `address` or (`ip` + `port`)
      '''
      if not address and ((ip and not port) or (not ip and port)):
         raise TypeError('You have to specifiy either (address) or (ip + port)')

      if not address and not ip and not port:
         self.ip = '127.0.0.1'
         self.port = 5440
         self.addr = (self.ip, self.port)
         self.hostType = 'UDP'

      elif not address and ip and port:
         self.ip = ip
         self.port = port
         self.addr = (ip, port)
         self.hostType = 'UDP'

      elif address and not ip and not port:
         self.ip = address[0]
         self.port = address[1]
         self.addr = address
         self.hostType = 'UDP'

      else:
         self.ip = ip
         self.port = port
         self.addr = (ip, port)
         self.hostType = 'UDP'

      self.bufferSize = bufferSize
      self.client = socket(AF_INET, SOCK_DGRAM)
      self._send(
         self._buildData(type='Handshake')
      )

   def _buildData(self, **kwargs):
      return convert(OBJ, PYON, {**kwargs})

   def _send(self, data:str):
      dataLength = f'{len(data)}'.encode('utf-8')
      data = data.encode('utf-8')

      self.client.sendto(dataLength, self.addr)
      self.client.sendto(data, self.addr)

   def _recv(self):
      dataLength, address = self.client.recvfrom(self.bufferSize)

      if dataLength:
         data, address = self.client.recvfrom(int(dataLength))
         data = data.decode('utf-8')

         if data.startswith('Error: '):
            raise ServerError(data)

         else:
            data = convert(PYON, OBJ, data)

            return data

   @property
   def databases(self) -> Dict[str, UDPDatabase]:
      self._send(
         self._buildData(type='getDatabases')
      )
      databases = self._recv()
      resultDict = {}

      for db in databases:
         if db.endswith('.sdb'):
            resultDict[db.replace('.sdb', '').strip()] = UDPDatabase(self.client, self.addr, db)
         if not db.endswith('.sdb'):
            resultDict[f'{db}.sdb'] = UDPDatabase(self.client, self.addr, db, self.bufferSize)

         resultDict[db] = UDPDatabase(self.client, self.addr, db, self.bufferSize)

      return resultDict

def getClassName(object):
   return object.__class__.__name__

def findDatabases(path:str):
   return list(map(lambda e:join(path, e), filter(lambda e:e.endswith('.sdb'), listdir(path))))

def allTypes(l:list, t):
   return all(isinstance(x, t) for x in l)