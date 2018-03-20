import http.client
import json

headers = {'User-Agent': 'http-client'}

conn = http.client.HTTPSConnection("https://api.fda.gov")
conn.request("GET","/drug/label.json" , None, headers)
r1 = conn.getresponse()
print(r1.status, r1.reason)
drugs_raw = r1.read().decode("utf-8")
conn.close()
drugs = json.loads(drugs_raw)
results = drugs["results"]
my_drug = results[0]
id_drug = my_drug["id"]
print("The id of the drug is", id_drug)
