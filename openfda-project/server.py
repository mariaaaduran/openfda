"""
OPENFDA FINAL PROJECT

Here is the code corresponding to the final project:

"""

import http.server
import json
import socketserver
import http.client

# We specify the PORT and IP, this´ll let us run the script.
socketserver.TCPServer.allow_reuse_address = True

PORT = 8000
IP = '127.0.0.1'


# We start defining the class OpenFDAClient:
class OpenFDAClient():
    def set_arguments(self, params):
        """
        The connection will be given to the direction: "api.fda.gov/drug/label.json" the parameters will be
        added to it, and will specify more the search
        """


        headers = {'User-Agent': 'http-client'}

        # Make a connection to the HTTPS client:
        con = http.client.HTTPSConnection("api.fda.gov")

        # The params, will let us give the client more specific results, the client must enter the query_url and add it the parameters to a more specific search.
        query_url = "/drug/label.json"
        if params:
            query_url += "?" + params

        print("fetching", query_url)

        con.request("GET", query_url, None, headers)

        response = con.getresponse()
        print("Status:", response.status, response.reason)
        data = response.read().decode("utf-8")
        con.close()

        # Now we put the results in json format:
        result = json.loads(data)
        return result['results'] if 'results' in result else []

    def search_drugs(self, active_ingredient, limit=10):
        """
        We define the search of the drugs, and the limit (10), only 10 items will appear       """
        params = 'search=active_ingredient:"{}"'.format(active_ingredient)

        if limit:
            params += "&limit=" + str(limit)
        drugs = self.set_arguments(params)
        return drugs["results"] if 'results' in drugs else []

    def search_companies_info(self, company_name, limit=10):
        """
        We do the same fo the search of the companies_info given a company_name with optional limit default is 10
        """
        params = 'search=openfda.manufacturer_name:"%s"' % company_name
        if limit:
            params += "&limit=" + str(limit)
        drugs = self.set_arguments(params)

        return drugs

    def list_drugs(self, limit=10):
        """
        We will botain the resquested list of drugs!!!
        """

        params = "limit=" + str(limit)

        drugs = self.set_arguments(params)

        return drugs



class OpenFDAParser():
    def parse_drugs(self, drugs):
        """
        The parse function  helps us to select only the items that the client wants. Thanks to it, we give the client a more specific response.
        We create a list ("drugs_labels") and we check that the drug wanted by the client in is the list and that it has his corresponding manufacturer_name.
        If these two steps are checked, we add to the list the drug, with the function append
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

    def parse_companies_info(self, drugs):
        """
        In this part we repite the steps as before, bu this time we are going to work with the companies´
        names and their corresponding drugs.
        As before we create a list and we check that the durg, the company, the manufacturer name, etc...exist
        If they do, we add, with the function append to our list ("Companies_info").
        """
        companies_info = []
        for drug in drugs:
            if 'openfda' in drug and 'manufacturer_name' in drug['openfda']:
                companies_info.append(drug['openfda']['manufacturer_name'][0])
            else:
                companies_info.append("Unknown")

            companies_info.append(drug['id'])

        return companies_info


    def parse_warnings(self, drugs):
        """
        To finish the part of the class OpenFDAParser(), we do the same but this time with the warnings.
        Create the list, the checking and finally the addition with the appennd function.
        """

        warnings = []

        for drug in drugs:
            if 'warnings' in drug and drug['warnings']:
                warnings.append(drug['warnings'][0])
            else:
                warnings.append("Unknown")
        return warnings



class OpenFDAHTML():
    def build_html_list(self, result):
        """
        At the class OpenFDAHTML we establish the html part.
        Also the web corresponding to the ERROR: not found
        """

        html_list = "<ul>"
        for item in result:
            html_list += "<li>" + item + "</li>"
        html_list += "</ul>"

        return html_list

    #ERROR HTML
    def show_page_not_found(self):
        with open("page_not_found.html") as html_file:
            return html_file.read()


class testHTTPRequestHandler(http.server.BaseHTTPRequestHandler):
    # Handle all the GET Requests
    def do_GET(self):
        """
        The server will response to the preferences of the client, giving his correspondant responses.
        """

        # First, we establish the object classes.
        client = OpenFDAClient()
        html_builder = OpenFDAHTML()
        json_parser = OpenFDAParser()

        #Generic response for any urls except the defined one
        response_code = 404
        response = html_builder.show_page_not_found()

        if self.path == "/":
            # This is to return to the home page
            with open("index.html") as f:
                response = f.read()

        if 'searchDrug' in self.path:
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
            result = client.search_drugs(active_ingredient, limit)
            response = html_builder.build_html_list(json_parser.parse_drugs(result))

        elif 'listDrugs' in self.path:
            limit = None
            if len(self.path.split("?")) > 1:
                limit = self.path.split("?")[1].split("=")[1]
            result = client.list_drugs(limit)
            response = html_builder.build_html_list(json_parser.parse_drugs(result))

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
            result = client.search_companies_info(company_name, limit)
            response = html_builder.build_html_list(json_parser.parse_companies_info(result))

        elif 'listCompanies' in self.path:
            limit = None
            if len(self.path.split("?")) > 1:
                limit = self.path.split("?")[1].split("=")[1]
            result = client.list_drugs(limit)
            response = html_builder.build_html_list(json_parser.parse_companies_info(result))

        elif 'listWarnings' in self.path:
            limit = None
            if len(self.path.split("?")) > 1:
                limit = self.path.split("?")[1].split("=")[1]
            result = client.list_drugs(limit)
            response = html_builder.build_html_list(json_parser.parse_warnings(result))

        if 'secret' in self.path:
            # set response code
            response_code = 401
            # send additonal header
            self.send_header('WWW-Authenticate', ' WWW-Authenticate de basic Realm')
        elif 'redirect' in self.path:
            # Set response code
            response_code = 302
            # Send redirect headers
            self.send_header('Location', 'http://localhost:8000/')

        # Send response status code:
        self.send_response(response_code)

        # Send headers:
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        # Show html response:
        self.wfile.write(bytes(response, "utf8"))


Handler = testHTTPRequestHandler

httpd = socketserver.TCPServer((IP, PORT), Handler)
print("serving at port", PORT)
httpd.serve_forever()