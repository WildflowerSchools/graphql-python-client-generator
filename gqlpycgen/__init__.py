from gqlpycgen.models import GraphEnum, filter_enums, Object, filter_objects, filter_interfaces, filter_unions, filter_scalars, Union, Scalar, filter_input_objects, InputObject
from gqlpycgen.loader import load_remote_schema


def write_header(out):
    out.write("# this file is generated, do not modify\n")
    out.write("from enum import Enum\n")
    out.write("from typing import List, NewType, TypeVar\n")
    out.write('\n')
    out.write('\n')
    out.write("ID = NewType('ID', str)\n")
    out.write("Int = NewType('Int', int)\n")
    out.write("String = NewType('String', str)\n")
    out.write("Float = NewType('Float', float)\n")
    out.write("Boolean = NewType('Boolean', bool)\n")


def do_remote(uri, filename):
    schema = load_remote_schema(uri)
    schema_types = schema.get("types")

    with open(filename, 'w') as out:
        write_header(out)

        for scalar in filter_scalars(schema_types):
            obj = Scalar(scalar)
            out.write(obj.toPython())

        out.write('\n')
        out.write('\n')

        for enumType in filter_enums(schema_types):
            enum = GraphEnum(enumType)
            out.write(enum.toPython())

        for objType in filter_input_objects(schema_types):
            obj = InputObject(objType)
            out.write(obj.toPython())

        for objType in filter_objects(schema_types):
            obj = Object(objType)
            out.write(obj.toPython())

        for objType in filter_interfaces(schema_types):
            obj = Object(objType)
            out.write(obj.toPython())

        for union in filter_unions(schema_types):
            obj = Union(union)
            out.write(obj.toPython())

        out.flush()

