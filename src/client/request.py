
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

    def handleResponse(self, request):

        status = request.status_code
        self.client.response_status = status
        headers = request.headers
        data = request.text

        # print('Status:', status)
        # print('Content:\n', data)
        # print('--------------------')

        content_type = headers['Content-Type']
        if content_type == 'application/json':
            data = json.loads(data)
            if 'client_data' in data.keys():
                # self.client.client_data = data['client_data']
                for i,j in data['client_data'].items():
                    self.client.client_data[i] = j
            if 'client_options' in data.keys():
                self.client.setClientOptions(data['client_options'])
            else:
                self.client.setClientOptions([])
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
        
        request = requests.get(url, headers={'Accept':'application/json'})
        self.handleResponse(request)
