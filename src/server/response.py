
import json
from http import HTTPStatus

class ServerResponse:

    status = HTTPStatus.OK
    headers = {}
    data = None

    def __init__(self, request):
        self.request = request

    def setStatus(self, status):
        self.status = status

    def setHeader(self, name, value):
        self.headers[name] = value

    def setContentType(self, type):
        self.setHeader('Content-Type', type)

    def setOutput(self, data):
        self.data = data

    def send(self):
        
        httpd = self.request.httpd

        data = self.data
        if isinstance(data, dict):
            data = json.dumps(data)
        data = bytes(data, 'utf-8')
        data_len = int(len(data))
        self.setHeader('Content-Length', data_len)

        # headers
        httpd.send_response(self.status)
        for header_key, header_val in self.headers.items():
            httpd.send_header(header_key, header_val)
        httpd.end_headers()

        # reply to client
        httpd.wfile.write(data)

