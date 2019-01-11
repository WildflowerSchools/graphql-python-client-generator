from collections import OrderedDict
from uuid import uuid4

import requests

from gqlpycgen.utils import json_dumps


class FileUpload(object):

    def __init__(self):
        # {"file": ["variables.file"]}
        self.map = dict()
        #     ('file', ('sandbox.py', open('sandbox.py', 'rb'), 'text/plain'))
        self.list = []
        self.containsFiles = False

    def add_file(self, var_path, filename, file, mimetype="application/octet-stream"):
        self.containsFiles = True
        file_id = uuid4().hex
        self.map[file_id] = [var_path]
        self.list.append((file_id, (filename, file, mimetype, ), ))


class Client(object):

    def __init__(self, uri):
        self.uri = uri

    def execute(self, query, variables=None, files=None):
        # print(query)
        payload = OrderedDict({
            'query': query,
            'variables': variables or {},
        })
        if files and files.containsFiles:
            data = {
                'operations': json_dumps(payload),
                'map': json_dumps(files.map),
            }
            request = requests.post(self.uri, data=data, files=files.list)
        else:
            request = requests.post(self.uri, data=json_dumps(payload), headers={'Content-Type': 'application/json'})
        request.raise_for_status()
        result = request.json()
        if "errors" in result:
            return result.get("errors")
        return result.get("data")
