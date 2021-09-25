# server

import os
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler
from http.server import HTTPServer
from src.server import ServerRequest
from src.server import HTTPMethod

class RockPaperScissorsRequestHandler(SimpleHTTPRequestHandler):
    """A custom HTTP Request Handler based on SimpleHTTPRequestHandler"""

    server_version = "My_HTTP_Server/"

    # constructor
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=os.getcwd(), **kwargs)  # initialize the base handler

    # GET
    def do_GET(self):
        """Serve a GET request."""
        self.request_type = HTTPMethod.GET
        request = ServerRequest(self)
        response = request.processRequest()
        response.send()

        # headers
        # self.send_response(HTTPStatus.OK)
        # self.end_headers()

        # reply to client
        # self.wfile.write(b"My Message!")


def runServer(port=8000):
    # server address
    server_address = ('', port)
    server = HTTPServer
    handler = RockPaperScissorsRequestHandler
    httpd = server(server_address, handler)
    httpd.serve_forever()

if __name__ == '__main__':
    if os.path.exists(os.getcwd()+"/game-data.json"):
        os.remove(os.getcwd()+"/game-data.json")
    os.system('clear')
    runServer()