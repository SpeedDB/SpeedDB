from os.path import isfile, abspath

schema = str({'__docs': []})

def makeDB(name:str):
   finalName = None

   if name.endswith('.sdb'):
      finalName = name
   else:
      finalName = f'{name}.sdb'

   if isfile(finalName):
      err = f'Error: {abspath(finalName)} already exists\n'

      return err

   with open(finalName, 'w') as file:
      file.write(schema)