
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
        if type == 'application/json':
            self.data = {}
        self.setHeader('Content-Type', type)

    def setOutput(self, data):
        self.data = data

    def print(self):
        print("{!s:-^50}\n{!s:->50}".format('Server Response',''))
        print('{!s:<18}{!s}'.format('Status:', self.status.value))
        print('{!s:<18}{!s}'.format('Content-Type:', self.headers['Content-Type']))
        print('{!s:<18}{!s}'.format('Content-Length:', self.headers['Content-Length']))
        print('{!s:<18}\n{!s}'.format('Data:', self.data))
        print("{!s:->50}".format(''))

    def send(self):
        
        httpd = self.request.httpd
        data = self.data
        if data != None:    
            if isinstance(data, dict):
                data = json.dumps(data)
            data = bytes(data, 'utf-8')
            data_len = int(len(data))
            self.setHeader('Content-Length', data_len)

        self.print()

        # headers
        httpd.send_response(self.status)
        for header_key, header_val in self.headers.items():
            httpd.send_header(header_key, header_val)
        httpd.end_headers()

        # reply to client
        if data != None:
            httpd.wfile.write(data)
        
        

