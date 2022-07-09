import requests

print(requests.post('http://127.0.0.1:5440/tests.sdb', data={'data': "{'name': 'Nawaf'}"}).text)