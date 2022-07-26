import collections
from datetime import datetime
from typing import Dict, get_type_hints, Union

from jinja2 import Template

from gqlpycgen.client import Client
from gqlpycgen.utils import json_dumps


MAX_DEPTH = 3
ISO_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"


def timestamp():
    return datetime.utcnow().strftime(ISO_FORMAT)


union_template = Template("""{{ pre_prefix }}{{ name }} {
{{ prefix }}{% for type_obj in types %}... on {{ type_obj.__name__ }} {{ '{' }}
{% for k, v in get_type_hints(type_obj.__init__).items() %}
{{ property_to_gql(type_obj, k, v, indent + 1, True) }}
{% endfor %}
{{ prefix }}{{ '}' }}
{% endfor %}
}
""")


def union_gql(union, name, indent):
    if indent > MAX_DEPTH:
        return ""
    prefix = ("    " * indent)
    pre_prefix = ("    " * (indent - 1))
    types = union.__args__[:-1]
    # TODO - known issue, for the case where two of the types have a property with the same name and the don't have the exact same type it blows up
    #   keep in mind String != String!
    # type_properties = dict()
    # for ty in types:
    #     props = dict()
    #     for k, v in get_type_hints(type_obj.__init__).items()
    #         props[k] = v
    #     type_properties[ty.__name__] = props
    return union_template.render(
        name=name,
        types=types,
        prefix=prefix,
        pre_prefix=pre_prefix,
        get_type_hints=get_type_hints,
        property_to_gql=property_to_gql,
        indent=indent,
    )


def property_to_gql(cls, name, value, indent, add_alias=False):
    if hasattr(value, "__origin__") and value.__origin__ is Union and len(value.__args__) > 2:
        # stupid hack, it seems python adds a NoneType as part of a Union for all
        return union_gql(value, name, indent + 1)
    if hasattr(value, "__args__"):
        value = value.__args__[0]
    if cls.TYPES[name].startswith("List["):
        value = value.__args__[0]
        if hasattr(value, "__args__"):
            value = value.__args__[0]
            if hasattr(value, "__args__"):
                value = value.__args__[0]
    if hasattr(value, 'gql'):
        return value.gql(name, indent + 1, None)
    else:
        return ("    " * indent) + name


class QueryBase(object):

    def __init__(self, client: Client):
        self.client = client

    def query(self, query: str, variables: Dict) -> Dict:
        gql_query = query
        try:
            results = self.client.execute(gql_query, variables)
            # TODO - handle error responses
            return results
        except Exception as err:
            print("-" * 80)
            print(query)
            print(json_dumps(variables))
            print(err)
            print("-" * 80)
            return {"status": "err", "message": str(err)}

    def prepare(self, cls, name, variables, var_types):
        if hasattr(cls, "gql"):
            gql = cls.gql(name, 1, variables)
            # TODO - need to make variable types match exactly, ID != ID! *sigh*
            args = ", ".join(["${}: {}".format(arg, var_types[arg].__name__) for arg in variables.keys()])
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
            elif value is not None:
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
            bits.append(property_to_gql(cls, k, v, indent))
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
            else:
                args[k] = None
        return cls(**args)
