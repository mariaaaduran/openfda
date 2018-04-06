
import socket

PORT = 8093
MAX_OPEN_REQUESTS = 5

def processing_client(clientsocket):
    import http.client
    import json

    headers = {'User-Agent': 'http-client'}

    conn = http.client.HTTPSConnection("api.fda.gov")
    conn.request("GET", "/drug/label.json?limit=10", None, headers)
    r1 = conn.getresponse()
    print(r1.status, r1.reason)
    repos_raw = r1.read().decode("utf-8")
    conn.close()

    repos = json.loads(repos_raw)

    list = []
    i = 0
    intro = "<ol>" + "\n"
    end = "<\ol>"

    while i < 10:
        if 'active_ingredient' in repos['results'][i]:
            i += 1
            list.append(repos['results'][i]['active_ingredient'][0])
        else:
            i += 1
            list.append("This index hasn´t any drug")

    with open("drug.html","w") as f:
        f.write(intro)
        for element in list:
            element_1 = "<\t>" + "<li>" + element + "<\li>"
            f.write(element_1)
        f.write(end)

    with open("drug.html","r") as f:
        file = f.read()

    web_contents = file
    web_headers = "HTTP/1.1 200"
    web_headers += "\n" + "Content-Type: text/html"
    web_headers += "\n" + "Content-Length: %i" % len(str.encode(web_contents))
    clientsocket.send(str.encode(web_headers + "\n\n" + web_contents))
    clientsocket.close()


serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

hostname = socket.gethostname()

hostname = "localhost"
try:
    serversocket.bind((hostname, PORT))
    serversocket.listen(MAX_OPEN_REQUESTS)

    while True:
        print ("Waiting for connections at %s %i" % (hostname, PORT))
        (clientsocket, address) = serversocket.accept()
        
        
        process_client(clientsocket)

except socket.error:
    print("Problemas using port %i. Permission?" % PORT)
