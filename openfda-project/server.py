import http.server
import http.client
import json
import socketserver

PORT=8000

class testHTTPRequestHandler(http.server.BaseHTTPRequestHandler): # Define el comportamiento de lo que tienes que hacer ante un apetición http. Tenemos el recurso doget
    # Constantes que he definido CAMBIAR NOMBRE
    OPENFDA_API_URL="api.fda.gov"
    OPENFDA_API_EVENT="/drug/label.json"
    OPENFDA_API_DRUG='&search=active_ingredient:'
    OPENFDA_API_COMPANY='&search=openfda.manufacturer_name:'


    def get_main_page(self):
        html = """
            <html>
                <head>
                    <title>OpenFDA App</title>
                </head>
                <body style='background-color: yellow'>
                    <h1>OpenFDA Client </h1>
                    <form method="get" action="listDrugs">
                        <input type = "submit" value="Drug List">
                        </input>
                    </form>
                    **************************************************
                    <form method="get" action="searchDrug">
                        <input type = "submit" value="Drug Search">
                        <input type = "text" name="drug"></input>
                        </input>
                    </form>
                    **************************************************
                    <form method="get" action="listCompanies">
                        <input type = "submit" value="Company List">
                        </input>
                    </form>
                    **************************************************
                    <form method="get" action="searchCompany">
                        <input type = "submit" value="Company Search">
                        <input type = "text" name="company"></input>
                        </input>
                    </form>
                    **************************************************
                    <form method="get" action="listWarnings">
                        <input type = "submit" value="Warnings List">
                        </input>
                    </form>
                </body>
            </html>
                """
        return html
    def dame_web (self, lista):
        list_html = """
                                <html>
                                    <head>
                                        <title>OpenFDA Cool App</title>
                                    </head>
                                    <body>
                                        <ul>
                            """
        for item in lista:
            list_html += "<li>" + item + "</li>"

        list_html += """
                                        </ul>
                                    </body>
                                </html>
                            """
        return list_html
    def dame_resultados_genericos (self, limit=10):
        connection = http.client.HTTPSConnection(self.OPENFDA_API_URL)
        connection.request("GET", self.OPENFDA_API_EVENT + "?limit="+str(limit))
        print (self.OPENFDA_API_EVENT + "?limit="+str(limit))
        resp1 = connection.getresponse()
        data_raw = resp1.read().decode("utf8")
        data = json.loads(data_raw)
        resultados = data['results']
        return resultados
    def do_GET(self): #es el metodo que se ejecuta de entrada, cuando alguien se conecte a la web y pida un get
        recurso_list = self.path.split("?")
        if len(recurso_list) > 1:
            params = recurso_list[1] #despues del split nos quedamos con la parte anterior al parametro, si existe algo despues del split será un parámetro guardado en params (xej un limit)
        else:
            params = ""

        limit = 1 #si no hubiese parámetros, no se especifica, el limit=1 por defecto

        # Obtener los parametros
        if params:
            parse_limit = params.split("=") #para sacar los parámetros hacemos un split por el igual
            if parse_limit[0] == "limit": # el parametro limit esta en el parametro 0
                limit = int(parse_limit[1]) #en la posición 1 estará el numero que es el limite
                print("Limit: {}".format(limit))
        else:
            print("SIN PARAMETROS")




        # Write content as utf-8 data
        if self.path=='/':
            # Send response status code
            self.send_response(200)
            # Send headers
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            html=self.get_main_page() #construye la web de los formularios y lo devuelve como un str
            self.wfile.write(bytes(html, "utf8"))
        elif 'listDrugs' in self.path:
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            medicamentos = []
            resultados = self.dame_resultados_genericos(limit)
            for resultado in resultados:
                if ('generic_name' in resultado['openfda']):
                    medicamentos.append (resultado['openfda']['generic_name'][0])
                else:
                    medicamentos.append('Desconocido')
            resultado_html = self.dame_web (medicamentos)

            self.wfile.write(bytes(resultado_html, "utf8"))
        elif 'listCompanies' in self.path:
            self.send_response(200)
            # Send headers
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            companies = []
            resultados = self.dame_resultados_genericos (limit)
            for resultado in resultados:
                if ('manufacturer_name' in resultado['openfda']):
                    companies.append (resultado['openfda']['manufacturer_name'][0])
                else:
                    companies.append('Desconocido')
            resultado_html = self.dame_web(companies)

            self.wfile.write(bytes(resultado_html, "utf8"))
        elif 'listWarnings' in self.path:
            # Send response status code
            self.send_response(200)

            # Send headers
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            warnings = []
            resultados = self.dame_resultados_genericos (limit)
            for resultado in resultados:
                if ('warnings' in resultado):
                    warnings.append (resultado['warnings'][0])
                else:
                    warnings.append('Desconocido')
            resultado_html = self.dame_web(warnings)

            self.wfile.write(bytes(resultado_html, "utf8"))
        elif 'searchDrug' in self.path:
            # Send response status code
            self.send_response(200)

            # Send headers
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            #Por defecto 10 en este caso, no 1
            limit = 10
            drug=self.path.split('=')[1]

            drugs = []
            connection = http.client.HTTPSConnection(self.OPENFDA_API_URL)
            connection.request("GET", self.OPENFDA_API_EVENT + "?limit="+str(limit) + self.OPENFDA_API_DRUG + drug)
            resp1 = connection.getresponse()
            data1 = resp1.read()
            data = data1.decode("utf8")
            biblioteca_data = json.loads(data)
            events_search_drug = biblioteca_data['results']
            for resultado in events_search_drug:
                if ('generic_name' in resultado['openfda']):
                    drugs.append(resultado['openfda']['generic_name'][0])
                else:
                    drugs.append('Desconocido')

            resultado_html = self.dame_web(drugs)
            self.wfile.write(bytes(resultado_html, "utf8"))
        elif 'searchCompany' in self.path:
            # Send response status code
            self.send_response(200)

            # Send headers
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            # Por defecto 10 en este caso, no 1
            limit = 10
            company=self.path.split('=')[1]
            companies = []
            connection = http.client.HTTPSConnection(self.OPENFDA_API_URL)
            connection.request("GET", self.OPENFDA_API_EVENT + "?limit=" + str(limit) + self.OPENFDA_API_COMPANY + company)
            resp1 = connection.getresponse()
            data1 = resp1.read()
            data = data1.decode("utf8")
            biblioteca_data = json.loads(data)
            events_search_company = biblioteca_data['results']

            for event in events_search_company:
                companies.append(event['openfda']['manufacturer_name'][0])
            resultado_html = self.dame_web(companies)
            self.wfile.write(bytes(resultado_html, "utf8"))
        elif 'redirect' in self.path:
            self.send_error(302)
            self.send_header('Location', 'http://localhost:'+str(PORT))
            self.end_headers()
        elif 'secret' in self.path:
            self.send_error(401)
            self.send_header('WWW-Authenticate', 'Basic realm="Mi servidor"')
            self.end_headers()
        else:
            self.send_error(404)
            self.send_header('Content-type', 'text/plain; charset=utf-8')
            self.end_headers()
            self.wfile.write("I don't know '{}'.".format(self.path).encode())
        return



socketserver.TCPServer.allow_reuse_address= True

Handler = testHTTPRequestHandler #instancia de una clase que puede respoder a dos peticiones http dtintas, un navegador y los test

httpd = socketserver.TCPServer(("", PORT), Handler) #asocia una ip y un puerto a tu manejador de peticiones. Cuando llega la peticion a la ip y puerto se manda automaticamente al maejador par que pueda responder a la peticion
print("serving at port", PORT)
httpd.serve_forever() #para que el servidor arranque y empiece a atender peticiones http