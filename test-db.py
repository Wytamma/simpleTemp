import requests
from datetime import datetime

url = 'http://127.0.0.1:5000/'

r = requests.post(url+'probes', data = {'probe_id':'example1'})
print(r.json())

r = requests.post(url+'records/example1', data = {'temperature':12.2, 'time':datetime.now().isoformat()})
print(r.json())

r = requests.get(url+'probes')
print(r.json())


r = requests.get(url+'records/example1')
print(r.json())
