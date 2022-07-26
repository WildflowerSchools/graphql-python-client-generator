from datetime import datetime, date
from enum import EnumMeta
import json


ISO_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"
DATE_FORMAT = "%Y-%m-%d"


def now():
    return datetime.utcnow().strftime(ISO_FORMAT)


def decode(val):
    if val and hasattr(val, "decode"):
        return val.decode("utf8")
    return val


class CustomJsonEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, bytes):
            return obj.decode("utf8")
        if isinstance(obj, datetime):
            return obj.strftime(ISO_FORMAT)
        if isinstance(obj, date):
            return obj.strftime(DATE_FORMAT)
        if hasattr(obj, "to_dict"):
            to_json = getattr(obj, "to_dict")
            if callable(to_json):
                return to_json()
        if hasattr(obj, "value"):
            return obj.value
        return json.JSONEncoder.default(self, obj)


def json_dumps(data, pretty=False):
    if pretty:
        return json.dumps(data, cls=CustomJsonEncoder, indent=4, sort_keys=True)
    return json.dumps(data, cls=CustomJsonEncoder)
