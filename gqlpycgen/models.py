import json

from jinja2 import Template


LF = '\n'
LFLF = '\n\n'
LFTABTAB = '\n        '


def resolve_type(typeObj):
    if typeObj.get("kind") == "LIST":
        return f'List[{typeObj.get("ofType").get("kind")}]'
    if typeObj.get("kind") == "NON_NULL":
        ofType = typeObj.get("ofType")
        if ofType.get("kind") == "LIST":
            return f'List[{resolve_type(ofType.get("ofType"))}]'
        else:
            return typeObj.get("ofType").get("name")
    elif typeObj.get("kind"):
        return typeObj.get("name")
    else:
        raise Warning(f'type {typeObj} is not understood')
        return None


class Field(object):

    def __init__(self, name, gtype):
        self.name = name
        self.gtype = gtype

    def __str__(self):
        return f"{self.name}: '{self.gtype}'"


objectTemplate = Template("""class {{name}}(ObjectBase):
    FIELDS = [{% for name in field_names %}"{{ name }}", {% endfor %}]
    TYPES = {{ '{' }}{% for field in fields %}"{{ field.name }}": "{{ field.gtype }}"{% if not loop.last %}, {% endif %}{% endfor %}{{ '}' }}

    def __init__(self, {% for field in fields %}{{ field }}{% if not loop.last %}, {% endif %}{% endfor %}):{% for field in fields %}
        self.{{ field.name }}: '{{ field.gtype }}' = {{ field.name }}{% endfor %}



""")


class Object(object):

    def __init__(self, typeObj):
        self.name = typeObj.get("name")
        self.field_names = [field.get("name") for field in typeObj.get("fields")]
        self.fields = []
        self.generate_argument_list(typeObj.get("fields"))

    def list_dependencies(self):
        deps = set()
        for field in self.fields:
            gtype = field.gtype
            if gtype.startswith("List"):
                gtype = gtype[5:-1]
            if gtype not in ["String", "Boolean", "Float", "Int", "ID"]:
                deps.add(gtype)
        return list(deps)

    def toPython(self):
        return objectTemplate.render(**self.__dict__)

    def generate_argument_list(self, fields):
        for field in fields:
            name = field.get("name")
            ftype = resolve_type(field.get("type"))
            if ftype:
                self.fields.append(Field(name, ftype))
            else:
                raise Warning(f'field {name} on {self.name}, type not understood')


class InputObject(Object):

    def __init__(self, typeObj):
        self.name = typeObj.get("name")
        self.field_names = [field.get("name") for field in typeObj.get("inputFields")]
        self.fields = []
        self.generate_argument_list(typeObj.get("inputFields"))


class GraphEnum(object):

    def __init__(self, typeObj):
        self.name = typeObj.get("name")
        self.values = [value.get("name") for value in typeObj.get("enumValues")]

    def toPython(self):
        props = [f'    {value} = "{value}"' for value in self.values]
        return f"""class {self.name}(Enum):
{LF.join(props)}

    def __str__(self):
        return str(self.value)


"""


class Union(object):

    def __init__(self, typeObj):
        self.name = typeObj.get("name")
        self.possible_types = [pt.get("name") for pt in typeObj.get("possibleTypes")]

    def toPython(self):
        return f"""{self.name} = Union[{", ".join(self.possible_types)}]\n"""


class Scalar(object):

    def __init__(self, typeObj):
        self.name = typeObj.get("name")

    def toPython(self):
        return f"{self.name} = NewType('{self.name}', str)\n"


queryMethodTemplate = Template("""
    def {{name}}(self, {% for arg in args %}{{ arg }}{% if not loop.last %}, {% endif %}{% endfor %}) -> {{ returns }}:
        args = [{% for arg in args %}"{{ arg }}"{% if not loop.last %}, {% endif %}{% endfor %}]
        variables = dict()
        var_types = dict()
{% for arg in args %}
        if {{ arg.name }} is not None:
            var_types["{{ arg.name }}"] = {{ arg.gtype }}
            if hasattr({{ arg.name }}, "to_json"):
                variables["{{ arg.name }}"] = {{ arg.name }}.to_json()
            else:
                variables["{{ arg.name }}"] = {{ arg.name }}
{% endfor %}
        query = self.prepare({{ returns }}, "{{ name }}", variables, var_types)
        results = self.query(query, variables)
        return {{ returns }}.from_json(results.get("{{ name }}"))
""")


class QueryMethod(object):

    def __init__(self, typeObj):
        self.name = typeObj.get("name")
        self.returns = resolve_type(typeObj.get("type"))
        self.args = []
        self.generate_argument_list(typeObj.get("args"))

    def generate_argument_list(self, fields):
        for field in fields:
            name = field.get("name")
            ftype = resolve_type(field.get("type"))
            if ftype:
                self.args.append(Field(name, ftype))
            else:
                raise Warning(f'arg {name} on {self.name}, type not understood')

    def toPython(self):
        return queryMethodTemplate.render(**self.__dict__)


class Query(object):

    def __init__(self, typeObj):
        self.methods = []
        for field in typeObj.get("fields"):
            if not field.get("name").startswith("_"):
                method = QueryMethod(field)
                self.methods.append(method)

    def toPython(self):
        return f"""class Query(QueryBase):
{LF.join([method.toPython() for method in self.methods])}
"""


class Mutation(object):

    def __init__(self, typeObj):
        self.methods = []
        for field in typeObj.get("fields"):
            if not field.get("name").startswith("_"):
                method = QueryMethod(field)
                self.methods.append(method)

    def toPython(self):
        return f"""class Mutation(MutationBase):
{LF.join([method.toPython() for method in self.methods])}
"""


def filter_enums(typeObjs):
    for typeObj in typeObjs:
        if not typeObj.get("name").startswith("_") and typeObj.get("kind") == "ENUM":
            yield typeObj


def filter_input_objects(typeObjs):
    for typeObj in typeObjs:
        if not typeObj.get("name").startswith("_") and typeObj.get("kind") == "INPUT_OBJECT":
            yield typeObj


def filter_objects(typeObjs):
    for typeObj in typeObjs:
        if not typeObj.get("name").startswith("_") and typeObj.get("kind") == "OBJECT" and typeObj.get("name") not in ["Query", "Mutation"]:
            yield typeObj


def filter_interfaces(typeObjs):
    for typeObj in typeObjs:
        if not typeObj.get("name").startswith("_") and typeObj.get("kind") == "INTERFACE":
            yield typeObj


def filter_unions(typeObjs):
    for typeObj in typeObjs:
        if not typeObj.get("name").startswith("_") and typeObj.get("kind") == "UNION":
            yield typeObj


def filter_scalars(typeObjs):
    for typeObj in typeObjs:
        if not typeObj.get("name").startswith("_") and typeObj.get("kind") == "SCALAR" and typeObj.get("name") not in ["String", "Int", "Boolean", "Float", "ID"]:
            yield typeObj
