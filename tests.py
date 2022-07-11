import speeddb

# client = speeddb.SpeedDBClient('http://localhost:5440')
# db = client.databases['tests']
db = speeddb.SpeedDBDatabase('db/tests.sdb')

document = db.get({'name': 'Nawaf'})

document['age'] = 10

db.update({'name': 'Nawaf'}, document)