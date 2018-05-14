import http.server
import json
import socketserver

socketserver.TCPServer.allow_reuse_address = True

PORT = 8000

OPENFDA_BASIC = False



class HTML():

    def create_list_html(self, things ):

        #We create a HTML list with parameters, also we´ll create de function to get a page not found fot the errors.


        listHTML = "<ul>"
        for item in things:
            listHTML += "<li>" + item + "</li>"
        listHTML += "</ul>"

        return listHTML


    def error_notfound(self):
        with open("not_found.html") as html_file:
            html = html_file.read()

        return html

class testHTTPRequestHandler(http.server.BaseHTTPRequestHandler):

    def with_GET(self):

        client = Client()
        html_vis = HTML()
        parser = Parser()

        http_answer_code = 200
        http_feedback = "<h1>Not supported</h1>"

        if self.path == "/":

            with open("openfda.html") as file_form:
                form = file_form.read()
                http_feedback = form
        elif 'searchDrug' in self.path:
            active_ingredient = None
            limit = 10
            params = self.path.split("?")[1].split("&")
            for param in params:
                param_name = param.split("=")[0]
                param_value = param.split("=")[1]
                if param_name == 'active_ingredient':
                    active_ingredient = param_value
                elif param_name == 'limit':
                    limit = param_value
            things = client.search_drugs(active_ingredient, limit)
            http_feedback = html_vis.create_html_list(parser.parse_drugs(things))
        elif 'listDrugs' in self.path:
            limit = None
            if len(self.path.split("?")) > 1:
                limit = self.path.split("?")[1].split("=")[1]
            things = client.list_drugs(limit)
            http_feedback = html_vis.create_html_list(parser.parse_drugs(things))
        elif 'searchCompany' in self.path:
            company_name = None
            limit = 10
            params = self.path.split("?")[1].split("&")
            for param in params:
                param_name = param.split("=")[0]
                param_value = param.split("=")[1]
                if param_name == 'company':
                    company_name = param_value
                elif param_name == 'limit':
                    limit = param_value
            things = client.search_companies(company_name, limit)
            http_feedback = html_vis.create_html_list(parser.parse_companies(things))
        elif 'listCompanies' in self.path:
            limit = None
            if len(self.path.split("?")) > 1:
                limit = self.path.split("?")[1].split("=")[1]
            things = client.list_drugs(limit)
            http_feedback = html_vis.create_html_list(parser.parse_companies(things))
        elif 'listWarnings' in self.path:
            limit = None
            if len(self.path.split("?")) > 1:
                limit = self.path.split("?")[1].split("=")[1]
            things = client.list_drugs(limit)
            http_feedback = html_vis.create_html_list(parser.parse_warnings(things))
        else:
            http_answer_code = 404
            if not OPENFDA_BASIC:
                url_found = False
                http_feedback = html_vis.error_notfound()

        # Send response status code
        self.send_response(http_answer_code)

        # Send the headers
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        # Write content as utf-8 data
        self.wfile.write(bytes(http_feedback, "utf8"))
        return

class Parser():

    def parse_companies(self, drugs):
        """
        Given a OpenFDA result, extract the drugs data
        :param drugs: result form a call to OpenFDA drugs API
        :return: list with companies info
        """

        companies = []
        for drug in drugs:
            if 'openfda' in drug and 'manufacturer_name' in drug['openfda']:
                companies.append(drug['openfda']['manufacturer_name'][0])
            else:
                companies.append("Unknown")

            companies.append(drug['id'])

        return companies

    def parse_drugs(self, drugs):
        """
        :param drugs: result form a call to OpenFDA drugs API
        :return: list with drugs info
        """

        drugs_labels = []

        for drug in drugs:
            drug_label = drug['id']
            if 'active_ingredient' in drug:
                drug_label += " " + drug['active_ingredient'][0]
            if 'openfda' in drug and 'manufacturer_name' in drug['openfda']:
                drug_label += " " + drug['openfda']['manufacturer_name'][0]

            drugs_labels.append(drug_label)

        return drugs_labels

    def parse_warnings(self, drugs):

        #Given a OpenFDA result, we take the warning data form the drugs


        warnings = []

        for drug in drugs:
            if 'warnings' in drug and drug['warnings']:
                warnings.append(drug['warnings'][0])
            else:
                warnings.append("None")
        return warnings




    class Client():

        def send_query(self, query):
            """
            Send a query to the OpenFDA API
            :param query: query to be sent
            :return: the result of the query in JSON format
            """

            headers = {'User-Agent': 'http-client'}

            conn = http.client.HTTPSConnection("api.fda.gov")

            # Get a  https://api.fda.gov/drug/label.json drug label from this URL and
            # extract what is the id,
            # the purpose of the drug and the manufacturer_name

            query_url = "/drug/label.json"

            if query:
                query_url += "?" + query

            print("Sending to OpenFDA the query", query_url)

            conn.request("GET", query_url, None, headers)
            r1 = conn.getresponse()
            print(r1.status, r1.reason)
            res_raw = r1.read().decode("utf-8")
            conn.close()

            res = json.loads(res_raw)

            if 'results' in res:
                things = res['results']
            else:
                things = []

            return things

        def search_drugs(self, active_ingredient, limit=10):
            """
            Search for drugs given an active ingredient drug_name
            :param drug_name: name of the drug to search
            :param limit: Number of items to be included in the list
            :return: a JSON list with the results
            """

            # drug_name for example: acetylsalicylic

            query = 'search=active_ingredient:"%s"' % active_ingredient

            if limit:
                query += "&limit=" + str(limit)

            drugs = self.send_query(query)
            return drugs

        def list_drugs(self, limit=10):
            """
            List default drugs
            :param limit: Number of items to be included in the list
            :return: a JSON list with the results
            """

            query = "limit=" + str(limit)

            drugs = self.send_query(query)

            return drugs

        def search_companies(self, company_name, limit=10):

            #Here we search companies given by the client

            query = 'search=openfda.manufacturer_name:"%s"' % company_name

            if limit:
                query += "&limit=" + str(limit)

            drugs = self.send_query(query)

            return drugs


Handler = testHTTPRequestHandler

httpd = socketserver.TCPServer(("", PORT), Handler)
print("serving at port", PORT)
httpd.serve_forever()

