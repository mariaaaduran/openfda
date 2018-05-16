
import http.server
import json
import socketserver

socketserver.TCPServer.allow_reuse_address = True

PORT = 8000

OPENFDA_BASIC = False

#In this part, we define the class html with the def function, we will create the web page (html) where
#the client will introduce his key words for the search.
#Each of the elements of the list is called with the variable "individual_component" and all of them together, "components_of_the_list".
class HTML():

    def create_list_HTML(self, components_of_the_list):

        list_web_components = "<ul>"
        for individual_component in components_of_the_list:
            list_web_components += "<li>" + individual_component + "</li>"
        list_web_components += "</ul>"

        return list_web_components


    def error_notfound(self):
        with open("not_found.html") as html_file:
            html = html_file.read()

        return html
#Now it´s the time of the Client part, we know that principal direction of the web is "api.fda.gov", followed by "/drug/label.json"
#This complete direction has access to all the list of the drugs, companies...But what we want to do is make easier the life to the client
#So if  the client enters a key word, the search will be more effective, this is the reason why the variable query is created.
class Client():

    def query_of_the_client(self, query):

        headers = {'User-Agent': 'http-client'}

        conn = http.client.HTTPSConnection("api.fda.gov")


        query_url = "/drug/label.json"

        #With this function we are allowing the client access to the url to introduce the query (key word for the search):
        if query:
            query_url += "?" + query

        print("The query introduced by the server is being sent:", query_url)

        conn.request("GET", query_url, None, headers)
        r1 = conn.getresponse()
        print(r1.status, r1.reason)
        #With the variable ... we read and the response given and then we decode it
        #to a standar format used in programming the "utf-8"
        answer_utf = r1.read().decode("utf-8")
        conn.close()

        answer = json.loads(answer_utf)
#Now with this lines we tell the server to answer with the list of components:
        if 'results' in answer:
            components_of_the_list = answer['results']
        else:
            components_of_the_list = []

        return components_of_the_list
#To define the search of drugs; we tell the client to enter a name of a drug and a limit, to know
#how many names of drugs he want to receive, the prgram will return the list with the results
#claimed by the patient:
    def search_drugs(self, active_ingredient, limit=10):

        query = 'search=active_ingredient:"%s"' % active_ingredient

        if limit:
            query += "&limit=" + str(limit)

        drugs_list = self.query_of_the_client(query)
        return drugs_list

    def list_drugs_limit(self, limit=10):
        """
        List default drugs
        :param limit: Number of items to be included in the list
        :return: a JSON list with the results
        """

        query = "limit=" + str(limit)

        drugs_list = self.query_of_the_client(query)

        return drugs_list

    def search_companies(self, company_name, limit=10):
        """
        Search for companies given a company_name
        :param company_name: name of the company to search
        :return: a JSON list with the results
        """

        query = 'search=openfda.manufacturer_name:"%s"' % company_name

        if limit:
            query += "&limit=" + str(limit)

        drugs_list = self.query_of_the_client(query)

        return drugs_list

class Parser():

    def parse_companies(self, drugs_list):
        """
        Given a OpenFDA result, extract the drugs data
        :param drugs: result form a call to OpenFDA drugs API
        :return: list with companies info
        """

        companies = []
        for drug in drugs_list:
            if 'openfda' in drug and 'manufacturer_name' in drug['openfda']:
                companies.append(drug['openfda']['manufacturer_name'][0])
            else:
                companies.append("Unknown")

            companies.append(drug['id'])

        return companies

    def parse_drugs(self, drugs_list):
        """
        :param drugs: result form a call to OpenFDA drugs API
        :return: list with drugs info
        """

        drugs_labels = []

        for drug in drugs_list:
            drug_label = drug['id']
            if 'active_ingredient' in drug:
                drug_label += " " + drug['active_ingredient'][0]
            if 'openfda' in drug and 'manufacturer_name' in drug['openfda']:
                drug_label += " " + drug['openfda']['manufacturer_name'][0]

            drugs_labels.append(drug_label)

        return drugs_labels

    def parse_warnings(self, drugs_list):
        """
        Given a OpenFDA result, extract the warnings data
        :param drugs: result form a call to OpenFDA drugs API
        :return: list with warnings info
        """

        warnings = []

        for drug in drugs_list:
            if 'warnings' in drug and drug['warnings']:
                warnings.append(drug['warnings'][0])
            else:
                warnings.append("None")
        return warnings


# HTTPRequestHandler class
class testHTTPRequestHandler(http.server.BaseHTTPRequestHandler):

    # GET
    def do_GET(self):
        """
        API to be supported
        searchDrug?drug=<drug_name>
        searchCompany?company=<company_name>
        listDrugs
        listCompanies
        listWarnings
        """

        client = Client()
        html_vis = HTML()
        parser = Parser()

        http_response_code = 200
        http_response = "<h1>Not supported</h1>"

        if self.path == "/":
            # Return the HTML form for searching
            with open("openfda.html") as file_form:
                form = file_form.read()
                http_response = form
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
            components_of_the_list = client.search_drugs(active_ingredient, limit)
            http_response = html_vis.create_list_HTML(parser.parse_drugs(components_of_the_list))
        elif 'listDrugs' in self.path:
            limit = None
            if len(self.path.split("?")) > 1:
                limit = self.path.split("?")[1].split("=")[1]
            components_of_the_list = client.list_drugs_limit(limit)
            http_response = html_vis.create_list_HTML(parser.parse_drugs(components_of_the_list))
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
            components_of_the_list = client.search_companies(company_name, limit)
            http_response = html_vis.create_list_HTML(parser.parse_companies(components_of_the_list))
        elif 'listCompanies' in self.path:
            limit = None
            if len(self.path.split("?")) > 1:
                limit = self.path.split("?")[1].split("=")[1]
            components_of_the_list = client.list_drugs_limit(limit)
            http_response = html_vis.create_list_HTML(parser.parse_companies(components_of_the_list))
        elif 'listWarnings' in self.path:
            limit = None
            if len(self.path.split("?")) > 1:
                limit = self.path.split("?")[1].split("=")[1]
            components_of_the_list = client.list_drugs_limit(limit)
            http_response = html_vis.create_list_HTML(parser.parse_warnings(components_of_the_list))
        else:
            http_response_code = 404
            if not OPENFDA_BASIC:
                url_found = False
                http_response = html_vis.error_notfound()

        # Send response status code
        self.send_response(http_response_code)

        # Send the headers
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        # Write content as utf-8 data
        self.wfile.write(bytes(http_response, "utf8"))
        return


Handler = testHTTPRequestHandler

httpd = socketserver.TCPServer(("", PORT), Handler)
print("serving at port", PORT)
httpd.serve_forever()
