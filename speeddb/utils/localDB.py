from os.path import abspath, basename, join, splitext
from os import listdir
from pyonr import read



def removeJunk(l:list[str], parentPath:str):
   return list(map(lambda e:join(parentPath, e), filter(lambda e:e.endswith('sdb'), l)))

def removeExt(file:str):
   return basename(file.removesuffix(splitext(file)[1]))

class LocalDB:
   def __init__(self, pathToDB:str):
      self.path = abspath(pathToDB)
      self.name = basename(self.path)
      self.pyonr = read(self.path)

class LocalDBs:
   def __init__(self, DBsPath:str):
      self.path = abspath(DBsPath)
      self.dbs = removeJunk(listdir(DBsPath), DBsPath)
      self.dbsWithoutExt = list(map(removeExt, self.dbs))
      self.dbsNames = list(map(basename, self.dbs))
      self.ldbs = list(map(LocalDB, self.dbs))

   def findDB(self, name:str):
      for db in self.ldbs:
         if db.name == name:
            return db