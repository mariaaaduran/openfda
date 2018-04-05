import http.server
import socketserver

# -- IP and the port of the server
IP = "localhost"  # Localhost means "I": your local machine
PORT = 8014


# HTTPRequestHandler class
class testHTTPRequestHandler(http.server.BaseHTTPRequestHandler):
    # GET
    def do_GET(self):
        # Send response status code
        self.send_response(200)

        # Send headers
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        if self.path == "/" :
            with open("index.html.","r") as f:
                index = f.read() 
                message = index
        elif self.path == "/new" :
            with open("new.html.","r") as f:
                new = f.read() 
                message = new
        else:
            with open("error.html.","r") as f:
                error = f.read() 
                message = error

        # Send message back to client
       
        # Write content as utf-8 data
        self.wfile.write(bytes(message, "utf8"))
        print("File served!")
        return


# Handler = http.server.SimpleHTTPRequestHandler
Handler = testHTTPRequestHandler

httpd = socketserver.TCPServer((IP, PORT), Handler)
print("serving at port", PORT)
try:
    httpd.serve_forever()
except KeyboardInterrupt:
        pass

httpd.server_close()
print("")
print("Server stopped!")


# https://github.com/joshmaker/simple-python-webserver/blob/master/server.py
