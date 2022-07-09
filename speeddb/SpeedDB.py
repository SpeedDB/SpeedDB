from pyonr import read
from uvicorn import run as runServer
from threading import Thread
from logging import ERROR
from socket import gethostbyname, gethostname
from os.path import abspath

from speeddb.utils.server import makeServer

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

   def _runServer(self):
      if not self.local:
         runServer(self.server, host='0.0.0.0', port=self.port, log_level=ERROR)
      else:
         runServer(self.server, port=self.port, log_level=ERROR)

   def _buildURL(self):
      url = 'http://'

      if self.local:
         url += '127.0.0.1'
      else:
         url += gethostbyname(gethostname()) # IPv4 Address
         
      url += f':{self.port}'

      return url

   def run(self, daemon:bool=False):


      if not daemon:
         print(f'SpeedDB Server is running on {self._buildURL()}')
         self._runServer()
      else:
         print(f'SpeedDB Server is running on {self._buildURL()}')
         thread = Thread(target=self._runServer, daemon=True, name='SpeedDB Server')

         self.thread = thread
         
         thread.start()
         
   # def shutdown(self):
   #    pass
         

class SpeedDBClient:
   pass



