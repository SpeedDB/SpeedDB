from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
from pyonr.converter import convert, PYON, OBJ
from pydantic import BaseModel
from typing import AnyStr

from .localDB import LocalDBs, LocalDB, removeJunk

class Data(BaseModel):
   data:AnyStr

def makeServer(dbsPath):
   app = FastAPI(title='SpeedDB', version='0.0.1b1')
   

   @app.get('/')
   def index():
      schema = {'err': False}
      
      ldbs = LocalDBs(dbsPath)
      dbs = list(map(lambda e:e.removesuffix('.sdb'), ldbs.dbsNames))

      schema['dbs'] = dbs
      
      return schema

   @app.get('/{dbName}')
   def dbGET(dbName:str):
      schema = {'err': False}

      ldbs = LocalDBs(dbsPath)
      dbs = ldbs.dbsNames
      dbsWithoutExt = ldbs.dbsWithoutExt
      
      if (dbName not in dbs) and (dbName not in dbsWithoutExt):
         schema['err'] = True
         schema['message'] = 'Invalid database name'
         
         return schema

      if dbName in dbsWithoutExt:
         dbName += '.sdb'
      
      return PlainTextResponse(f'{convert(PYON, OBJ, ldbs.findDB(dbName).pyonr.read)}')

   @app.post('/{dbName}')
   async def dbPOST(dbName:str, request:Request):
      schema = {'err': False}

      ldbs = LocalDBs(dbsPath)
      dbs = ldbs.dbsNames
      dbsWithoutExt = ldbs.dbsWithoutExt
      
      if (dbName not in dbs) and (dbName not in dbsWithoutExt):
         schema['err'] = True
         schema['message'] = 'Invalid database name'
         
         return schema

      if dbName in dbsWithoutExt:
         dbName += '.sdb'

      db = ldbs.findDB(dbName)

      data = await request.form()
      data = data._dict

      db.pyonr.write(data['data'])
      
      return schema

   return app