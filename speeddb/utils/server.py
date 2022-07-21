import socket
from pyonr.converter import convert, PYON, OBJ
from pyonr import read
from os import listdir
from os.path import split, join
from datetime import datetime

from .database import schema as SCHEMA

def algorithm(documents, _filter):
   return [d for d in documents if sum(1 for k, v in d.items() if _filter.get(k)==v) >= len(_filter)]

def findDatabases(path:str):
   return list(map(lambda e:join(path, e), filter(lambda e:e.endswith('.sdb'), listdir(path))))

def findDatabasePath(databases:list, dbname):
   for db in databases:
      dbFilename = split(db)[1]
      
      if dbFilename == dbname:
         return db

def cleanDatabasePath(db:str):
   return split(db)[1]

def send(socket, data:str, address:tuple, encoding:str='utf-8'):
   if isinstance(data, str) and data.startswith('Error: '):
      dataLength = f'{len(data)}'.encode('utf-8')
      data = data.encode('utf-8')

      socket.sendto(dataLength, address)
      socket.sendto(data, address)

   else:
      dataLength = f'{len(str(data))}'.encode(encoding)
      data = f'{data}'.encode(encoding)

      socket.sendto(dataLength, address)
      socket.sendto(data, address)

def readfile(readObj):
   return readObj.read

def writefile(readObj, update):
   readObj.write(update)

def UDPServer(server:socket.socket, dbsPath:str):
   BUFFERSIZE = 1024
   ENCODING = 'utf-8'

   connected = True
   while connected:
      dataLength, address = server.recvfrom(BUFFERSIZE)

      if dataLength:
         data, address = server.recvfrom(int(dataLength))
         data = convert(PYON, OBJ, data.decode(ENCODING))

         if data['type'] == 'Handshake':
            print(f'Received Handshake at {datetime.now().isoformat()}!')
            continue

         if data['type'] == 'getDatabases':
            databases = list(map(cleanDatabasePath, findDatabases(dbsPath)))

            send(server, databases, address, ENCODING)
            continue

         dbName = data['dbName']

         if not dbName.endswith('.sdb'):
            dbName += '.sdb'

         dbs = findDatabases(dbsPath)
         dbRelPath = findDatabasePath(dbs, dbName)

         if not dbRelPath:
            send(server, f'Error: No such database: {dbName}', address, ENCODING)
            continue

         readObj = read(dbRelPath)

         if data['type'] == 'get':
            _filter = data['data']

            if not isinstance(_filter, dict):
               send(server, f'Unexpected filter type: "{_filter.__class__.__name__}"', address, ENCODING)
               continue

            filedata = readfile(readObj)
            wantedData = algorithm(filedata['__docs'], _filter)
            wantedData = None if not wantedData else wantedData[0]
            
            send(server, wantedData, address, ENCODING)

         if data['type'] == 'getMany':
            _filter = data['data']

            if not isinstance(_filter, dict):
               send(server, f'Unexpected filter type: "{_filter.__class__.__name__}"', address, ENCODING)
               continue

            filedata = readfile(readObj)
            wantedData = algorithm(filedata['__docs'], _filter)

            send(server, wantedData, address, ENCODING)

         if data['type'] == 'append':
            document = data['data']

            if not isinstance(document, dict):
               send(server, f'Unexpected document type: "{document.__class__.__name__}"', address, ENCODING)
               continue

            filedata = readfile(readObj)
            filedata['__docs'].append(document)
            writefile(readObj, filedata)
            
         if data['type'] == 'appendMany':
            documents = data['data']

            if not isinstance(documents, list):
               send(server, f'Unexpected documents type: "{documents.__class__.__name__}"', address, ENCODING)
               continue

            filedata = readfile(readObj)
            filedata['__docs'].extend(documents)
            writefile(readObj, filedata)

         if data['type'] == 'remove':
            _filter = data['data']

            if not isinstance(_filter, dict):
               send(server, f'Unexpected filter type: "{_filter.__class__.__name__}"', address, ENCODING)
               continue

            filedata = readfile(readObj)
            fullDocument = algorithm(filedata['__docs'], _filter)

            if not fullDocument:
               continue

            fullDocument = fullDocument[0]
            filedata['__docs'].remove(fullDocument)
            writefile(readObj, filedata)

         if data['type'] == 'removeMany':
            _filter = data['data']

            if not isinstance(_filter, dict):
               send(server, f'Unexpected filter type: "{_filter.__class__.__name__}"', address, ENCODING)
               continue

            if _filter == {}:
               writefile(readObj, SCHEMA)
            else:
               filedata = readfile(readObj)
               documents = algorithm(filedata['__docs'], _filter)

               for doc in documents:
                  filedata['__docs'].remove(doc)

               writefile(readObj, filedata)

         if data['type'] == 'update':
            _filter = data['data']
            update = data.get('update')

            if not isinstance(update, dict):
               send(server, f'Unexpected update type: "{update.__class__.__name__}"', address, ENCODING)
               continue

            filedata = readfile(readObj)
            fullDocument = algorithm(filedata['__docs'], _filter)

            if not fullDocument:
               continue

            fullDocument = fullDocument[0]
            documentIndex = filedata['__docs'].index(fullDocument)
            filedata['__docs'][documentIndex] = update
            writefile(readObj, filedata)

   server.close()

def RunUDPServer(databasesPath:str, local:bool=True, port:int=5440):
   HOST = '0.0.0.0' if not local else '127.0.0.1'
   PORT = port
   ADDR = (HOST, PORT)

   server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
   server.bind(ADDR)

   UDPServer(server, databasesPath)

   server.shutdown(socket.SHUT_RDWR)
   server.close()