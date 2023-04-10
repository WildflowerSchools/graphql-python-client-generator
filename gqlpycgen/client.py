from collections import OrderedDict
from uuid import uuid4

from cachetools import TTLCache
import logging
import requests
import tenacity
import time

from gqlpycgen.utils import json_dumps

logger = logging.getLogger(__name__)

exponential_retry = tenacity.retry(
    stop=tenacity.stop_after_attempt(4),
    wait=tenacity.wait_exponential(multiplier=0.2 / 2),
    before=tenacity.before_log(logger, logging.DEBUG),
    after=tenacity.after_log(logger, logging.DEBUG),
    before_sleep=tenacity.before_sleep_log(logger, logging.WARNING),
)

DEFAULT_HTTP_REQUEST_TIMEOUT = 30  # HTTP request timeout in seconds


class FileUpload(object):
    def __init__(self):
        self.map = dict()
        self.list = []
        self.containsFiles = False

    def add_file(self, var_path, filename, file, mimetype="application/octet-stream"):
        self.containsFiles = True
        file_id = uuid4().hex
        self.map[file_id] = [var_path]
        self.list.append(
            (
                file_id,
                (
                    filename,
                    file,
                    mimetype,
                ),
            )
        )


class Client(object):
    def __init__(self, uri, accessToken=None, client_credentials=None, timeout=DEFAULT_HTTP_REQUEST_TIMEOUT):
        self.uri = uri
        self.client_credentials = client_credentials
        self.timeout = timeout
        self.headers = {"Content-Type": "application/json"}

        self.tokens = {}
        if accessToken is not None:
            self.tokens["access_token"] = accessToken

        if accessToken is None and self.client_credentials is None:
            raise ValueError("Cannot instantiate Honeycomb Client without an accessToken or client_credentials")

    def refresh_token(self):
        try:
            auth_response = requests.post(
                self.client_credentials["token_uri"],
                {
                    "audience": self.client_credentials["audience"],
                    "grant_type": "client_credentials",
                    "client_id": self.client_credentials["client_id"],
                    "client_secret": self.client_credentials["client_secret"],
                },
                timeout=self.timeout,
            ).json()

            access_token = auth_response.get("access_token", None)
            if access_token is None:
                raise Exception("invalid client_credentials")

            # Refresh token once TTL is less than 5 minutes
            self.tokens = TTLCache(maxsize=1, ttl=auth_response.get("expires_in") - 300)
            self.tokens["access_token"] = access_token

        except Exception as err:
            import traceback

            logger.error("An exception occured during Authorization")
            traceback.print_exception(err)
            raise Exception("invalid client_credentials") from err

    @property
    def headers(self):
        if "access_token" not in self.tokens:
            self.refresh_token()

        return {"Authorization": f"Bearer {self.tokens['access_token']}", **self._headers}

    @headers.setter
    def headers(self, header_dict: dict):
        self._headers = header_dict

    @exponential_retry
    def execute(self, query, variables=None, files=None, timeout=DEFAULT_HTTP_REQUEST_TIMEOUT):
        overall_start = time.time()
        logger.debug("Client execute request body JSON:\n{}".format(query))
        logger.debug("Client execute request variables JSON:\n{}".format(json_dumps(variables)))
        payload = OrderedDict(
            {
                "query": query,
                "variables": variables or {},
            }
        )
        if files and files.containsFiles:
            file_processing_start = time.time()
            data = {
                "operations": json_dumps(payload),
                "map": json_dumps(files.map),
            }
            file_processing_time = time.time() - file_processing_start
            post_start = time.time()
            request = requests.post(self.uri, data=data, files=files.list, headers=self.headers, timeout=timeout)
            post_time = time.time() - post_start
        else:
            file_processing_time = 0.0
            data = json_dumps(payload)
            post_start = time.time()
            request = requests.post(self.uri, data=data, headers=self.headers, timeout=timeout)
            post_time = time.time() - post_start
        request.raise_for_status()
        json_extraction_start = time.time()
        result = request.json()
        json_extraction_time = time.time() - json_extraction_start
        if "errors" in result:
            return result.get("errors")
        overall_time = time.time() - overall_start
        logger.info(
            "GraphQL client execute operation completed in {:.1f} ms (file processing: {:.1f} ms, POST operation: {:.1f} ms, JSON extraction: {:.1f} ms)".format(
                overall_time * 1000, file_processing_time * 1000, post_time * 1000, json_extraction_time * 1000
            )
        )
        return result.get("data")
