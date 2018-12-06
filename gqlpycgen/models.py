import json

LF = '\n'
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
        return f"""class {self.name}(object):
    FIELDS = {json.dumps(self.field_names)}

    def __init__(self, {", ".join(map(str, self.fields))}):
        {LFTABTAB.join(map(lambda name: f'self.{name} = {name}', self.field_names))}


"""

    def generate_argument_list(self, fields):
        for field in fields:
            name = field.get("name")
            ftype = resolve_type(field.get("type"))
            if ftype:
                self.fields.append(Field(name, ftype))
            else:
                raise Warning(f'field {name} on {self.name}')


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
        return f"""{self.name} = TypeVar('{self.name}', {", ".join(self.possible_types)})\n"""


class Scalar(object):

    def __init__(self, typeObj):
        self.name = typeObj.get("name")

    def toPython(self):
        return f"{self.name} = NewType('{self.name}', str)\n"


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
