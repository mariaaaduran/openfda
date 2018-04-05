import http.client
import json

headers = {'id': 'http-client'}

conn = http.client.HTTPSConnection("api.fda.gov")
conn.request("GET", "/drug/event.json?search=salycilic", None, headers)
r1 = conn.getresponse()
print(r1.status, r1.reason)
drugs_raw = r1.read().decode("utf-8")
conn.close()
drugs = json.loads(repos_raw)
drugs = drugs['results']
for element in drugs:
    print("The manufacturer names of the drugs that contain salycilic acid are:",drugs[0]['patient']['drug'][1]['openfda']['manufacturer_name'])
