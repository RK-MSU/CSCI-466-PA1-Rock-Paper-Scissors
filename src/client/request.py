
import json
import requests

class ClientRequest:

    default_headers = {
        'Accept': 'application/json'
    }

    def __init__(self, client):
        self.client = client

    def makeURL(self, path=None, qs=None):
        
        url = "http://%s:%s/" % (self.client.host, self.client.port)

        if path != None:
            if isinstance(path, str):
                url = "{}{}".format(url, path.strip('/'))
            if isinstance(path, list):
                url = "{}{}".format(url, "/".join(path))

        if qs != None and isinstance(qs, dict):
            qs_items = []
            for i,j in qs.items():
                qs_items.append("%s=%s" % (i,j))

            url += "/?" + "&".join(qs_items)

        return url

    def handleResponse(self, response):

        status = response.status_code
        content_len = response.headers['Content-Length']
        data = response.text

        content_type = response.headers['Content-Type']
        if content_type == 'application/json':
            data = json.loads(data) # TODO: add error

            if 'client_data' in data.keys():
                client_data = data['client_data']
                for i,j in client_data.items():
                    self.client.client_data[i] = j
                    # setattr(self.client, i, j)

            if 'client_options' in data.keys():
                self.client.client_options = data['client_options']

            if 'message' in data.keys():
                self.client.message = data['message']
            else:
                self.client.message = None

    def get(self, **kwargs):
        path = None
        if 'path' in kwargs.keys():
            path = kwargs['path']
        qs = None
        if 'qs' in kwargs.keys():
            qs = kwargs['qs']
        url = self.makeURL(path, qs)
        req = requests.get(url, headers={'Accept':'application/json'})
        self.handleResponse(req)
