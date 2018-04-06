import http.client
import json

headers = {'id': 'http-client'}

conn = http.client.HTTPSConnection("api.fda.gov")
conn.request("GET","/drug/label.json" , None, headers)
r1 = conn.getresponse()
print(r1.status, r1.reason)
drugs_raw = r1.read().decode("utf-8")
conn.close()
drugs = json.loads(drugs_raw)

drugs = drugs["results"]

https://api.fda.gov/drug/event.json?limit=10
