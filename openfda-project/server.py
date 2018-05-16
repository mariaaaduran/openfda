
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
    def looking_for_drugs(self, active_ingredient, limit=10):

        query = 'search=active_ingredient:"%s"' % active_ingredient

        if limit:
            query += "&limit=" + str(limit)

        drugs_list = self.query_of_the_client(query)
        return drugs_list
#Now it´s the turn to incoporate the function limit, so the client doesn´t receive all the list, only
#the number of drugs that he want, if he introduces 10 as the limit, he will receive 10 drugs.
    def list_drugs_limit(self, limit=10):

        query = "limit=" + str(limit)

        drugs_list = self.query_of_the_client(query)

        return drugs_list
#Now we have to do the same procedement that with the function defined by us called "looking_for_drugs" but with
#the name of the companies to which these drugs belong to.
#As before, the client must enter the name of the company and it ´ll be retuned a list with all the names of the companies.
    def looking_for_companies_limit(self, company_name, limit=10):

        query = 'search=openfda.manufacturer_name:"%s"' % company_name
#Now we have to limitate the number of companies name that the client will receive in function of his preferences, and we do
#the same procedement as with the limit of the list of drugs.
        if limit:
            query += "&limit=" + str(limit)

        drugs_list = self.query_of_the_client(query)

        return drugs_list
#Now we create the class Parser.
#The function parser is normally using in programming to take those items in which we are interested
#discarding the rest of items.

class Parser():

#With this function basically we are joinning the drug wuth the company, given the preferences of the client
#th drugs´ files will be extracted and then the information corresponding to the list of companies.

    def parse_drugs(self, drugs_list):
#We create the list as before, in this case called "drugs_wanted":
        drugs_wanted = []
#The first step to check is if the drug is in our list:
        for drug in drugs_list:
#Then we´ll must check if the drug wanted has a corresponding active ingredient, if it has, it´ll return it:
            drug_wanted = drug['id']
            if 'active_ingredient' in drug:
                drug_wanted += " " + drug['active_ingredient'][0]
#To finsh we´ll also check if the durg has a corresponding manufacturer name:
            if 'openfda' in drug and 'manufacturer_name' in drug['openfda']:
                drug_wanted += " " + drug['openfda']['manufacturer_name'][0]
#And if all this steps are OK, we´ll add to our list created the drug wanted:
            drugs_wanted.append(drug_wanted)

        return drugs_wanted



    def parse_companies(self, drugs_list):
#First of all we create a list. If we find that the drug introduced by the client is in the list
#the next step will be see if it has a corresponding manufacturer_name.
#If this two steps are OK, the last step will be add these files to the list "Companies" with the function append:
        companies_info = []
        for drug in drugs_list:
            if 'openfda' in drug and 'manufacturer_name' in drug['openfda']:
                companies_info.append(drug['openfda']['manufacturer_name'][0])
#If this two steps are not followed, we will add to the list the message of "It has been an error...", because the client
#will be asking by a drug that is not in our list or that it doensn´t have its corresponding manufacturer name.
            else:
                companies_info.append("There has been an error, check if you drug is in the list!")

            companies_info.append(drug['id'])

        return companies_info
#Now instead of obtain the name of the companies corresponding to the drugs that the client wants,
#We´ll only obtain the durgs corresponding to their names introduced by the client.


#And to finish the class parser, we do the same procedement that with the companies´ names and with the drugs, but this time with the warnings:
    def parse_warnings(self, drugs_list):
#We create our list, in this case called "warnings" and we check if the durg wanted is in our list and if
#it has corresponding warnings it will add to our thist the info, if not, it will return the message that there is an error:
        warnings_info = []

        for drug in drugs_list:
            if 'warnings' in drug and drug['warnings']:
                warnings_info.append(drug['warnings'][0])
            else:
                warnings_info.append("There has been an error, check if your drug is in the list!")
        return warnings_info



#To finsh we stablish the class testHTTPRequestHandler:
class testHTTPRequestHandler(http.server.BaseHTTPRequestHandler):
    def get_function(self):
        """
        API to be supported
        searchDrug?drug=<drug_name>
        searchCompany?company=<company_name>
        listDrugs_wanted
        listCompanies_info
        listWarnings_info
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
            components_of_the_list = client.looking_for_drugs(active_ingredient, limit)
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
            components_of_the_list = client.looking_for_companies_limit(company_name, limit)
            http_response = html_vis.create_list_HTML(parser.parse_companies(components_of_the_list))
        elif 'listCompanies_info' in self.path:
            limit = None
            if len(self.path.split("?")) > 1:
                limit = self.path.split("?")[1].split("=")[1]
            components_of_the_list = client.list_drugs_limit(limit)
            http_response = html_vis.create_list_HTML(parser.parse_companies(components_of_the_list))
        elif 'listWarnings_info' in self.path:
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
