import collections
from typing import Dict, get_type_hints

# from gql import Client, gql
# from gql.transport.requests import RequestsHTTPTransport

from gqlpycgen.client import Client

MAX_DEPTH = 3


class QueryBase(object):

    def __init__(self, uri: str):
        self.uri = uri
        # self.client = Client(transport=RequestsHTTPTransport(uri, use_json=True))
        self.client = Client(uri)

    def query(self, query: str, variables: Dict) -> Dict:
        print(query)
        gql_query = query
        # gql_query = gql(query)
        results = self.client.execute(gql_query, variables)
        print(results)
        return results

    def prepare(self, cls, name, variables, var_types):
        if hasattr(cls, "gql"):
            gql = cls.gql(name, 1, variables)
            args = ", ".join(["${}: {}".format(arg, var_types[arg]) for arg in variables.keys()])
            if len(variables):
                return "query %s (%s) { %s }" % (name, args, gql)
            else:
                return "query { %s }" % (gql)
        else:
            return "query { %s }" % (name)


class MutationBase(QueryBase):

    def prepare(self, cls, name, variables, var_types):
        if hasattr(cls, "gql"):
            gql = cls.gql(name, 1, variables)
            args = ", ".join(["${}: {}".format(arg, var_types[arg].__name__) for arg in variables.keys()])
            if len(variables):
                return "mutation %s (%s) { %s }" % (name, args, gql)
            else:
                return "mutation { %s }" % (gql)
        else:
            return "mutation { %s }" % (name)


class ObjectBase(object):

    def to_json(self) -> Dict:
        result = {}
        for k in self.FIELDS:
            value = getattr(self, k)
            if isinstance(value, list):
                result[k] = value
                if len(value) and hasattr(value[0], "to_json"):
                    result[k] = [v.to_json() for v in value]
            elif hasattr(value, "to_json"):
                result[k] = value.to_json()
            else:
                result[k] = value
        return result

    @classmethod
    def gql(cls, name: str, indent: int, variables: Dict) -> str:
        if indent > MAX_DEPTH:
            return ""
        bits = []
        prefix = ("    " * indent)
        pre_prefix = ("    " * (indent - 1))
        if variables and len(variables):
            bits.append(pre_prefix + name + "(" + ", ".join(["{}: ${}".format(arg, arg) for arg in variables.keys()]) + ") {")
        else:
            bits.append(pre_prefix + name + " {")
        hints = get_type_hints(cls.__init__)
        for k, v in hints.items():
            if cls.TYPES[k].startswith("List["):
                v = v.__args__[0]
            if hasattr(v, 'gql'):
                bits.append(v.gql(k, indent + 1, None))
            else:
                bits.append(prefix + k)
        bits.append(pre_prefix + "}")
        return "\n".join(bits)

    @classmethod
    def from_json(cls, obj: Dict):
        if obj is None:
            return None
        args = {}
        hints = get_type_hints(cls.__init__)
        for k, v in hints.items():
            if k in obj:
                if cls.TYPES[k].startswith("List["):
                    values = obj[k]
                    v = v.__args__[0]
                    if hasattr(v, 'from_json'):
                        args[k] = []
                        for value in values:
                            args[k].append(v.from_json(value))
                    else:
                        args[k] = values
                elif hasattr(v, 'from_json'):
                    args[k] = v.from_json(obj[k])
                else:
                    args[k] = obj[k]
        return cls(**args)
