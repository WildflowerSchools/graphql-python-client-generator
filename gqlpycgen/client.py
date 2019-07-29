from collections import OrderedDict
from uuid import uuid4

import requests

from gqlpycgen.utils import json_dumps


class FileUpload(object):

    def __init__(self):
        self.map = dict()
        self.list = []
        self.containsFiles = False

    def add_file(self, var_path, filename, file, mimetype="application/octet-stream"):
        self.containsFiles = True
        file_id = uuid4().hex
        self.map[file_id] = [var_path]
        self.list.append((file_id, (filename, file, mimetype, ), ))


class Client(object):

    def __init__(self, uri, accessToken=None, client_credentials=None):
        self.uri = uri
        self.accessToken = accessToken
        self.client_credentials = client_credentials
        self.headers = {'Content-Type': 'application/json'}
        self.headers_files = {}
        if self.accessToken:
            self.headers["Authorization"] = self.headers_files["Authorization"] = f'bearer {self.accessToken}'
        elif self.accessToken is None and self.client_credentials:
            try:
                auth_response = requests.post(client_credentials["token_uri"], {
                    "audience": client_credentials["audience"],
                    "grant_type": "client_credentials",
                    "client_id": client_credentials["client_id"],
                    "client_secret": client_credentials["client_secret"],
                })
                self.accessToken = auth_response.json().get('access_token')
                if self.accessToken:
                    self.headers["Authorization"] = self.headers_files["Authorization"] = f'bearer {self.accessToken}'
                else:
                    raise Exception("invalid client_credentials")
            except Exception as err:
                # TODO log this error
                raise Exception("invalid client_credentials")

    def execute(self, query, variables=None, files=None):
        payload = OrderedDict({
            'query': query,
            'variables': variables or {},
        })
        if files and files.containsFiles:
            data = {
                'operations': json_dumps(payload),
                'map': json_dumps(files.map),
            }
            request = requests.post(self.uri, data=data, files=files.list, headers=self.headers_files)
        else:
            request = requests.post(self.uri, data=json_dumps(payload), headers=self.headers)
        request.raise_for_status()
        result = request.json()
        if "errors" in result:
            return result.get("errors")
        return result.get("data")
