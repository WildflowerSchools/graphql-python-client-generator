from gqlpycgen.models import GraphEnum, filter_enums, Object, filter_objects, \
    filter_interfaces, filter_unions, filter_scalars, Union, Scalar, \
    filter_input_objects, InputObject, Query, Mutation
from gqlpycgen.loader import load_remote_schema


def write_header(out):
    out.write("# this file is generated, do not modify\n")
    out.write("from enum import Enum\n")
    out.write("from typing import List, NewType, TypeVar, Union\n")
    out.write('\n')
    out.write('from gqlpycgen.api import QueryBase, ObjectBase, MutationBase\n')
    out.write('\n')
    out.write('\n')
    out.write("ID = NewType('ID', str)\n")
    out.write("ID__Required = NewType('ID!', str)\n")
    out.write("Int = NewType('Int', int)\n")
    out.write("Int__Required = NewType('Int!', int)\n")
    out.write("String = NewType('String', str)\n")
    out.write("String__Required = NewType('String!', str)\n")
    out.write("Float = NewType('Float', float)\n")
    out.write("Float__Required = NewType('Float!', float)\n")
    out.write("Boolean = NewType('Boolean', bool)\n")
    out.write("Boolean__Required = NewType('Boolean!', bool)\n")


def do_remote(uri, filename, py36plus=True):
    schema = load_remote_schema(uri)
    schema_types = schema.get("types")

    with open(filename, 'w') as out:
        # includes the imports required and the core scalars
        write_header(out)

        # Pull all the scalars, filter_scalars skips the core primitives since we cover that in the headers
        for scalar in filter_scalars(schema_types):
            obj = Scalar(scalar)
            out.write(obj.toPython(py36plus=py36plus))

        # for PEP8
        out.write('\n')
        out.write('\n')

        # Pull all the ENUMs, turns them into python ENUM objects
        for enumType in filter_enums(schema_types):
            enum = GraphEnum(enumType)
            out.write(enum.toPython(py36plus=py36plus))

        # Pull interfaces, treat them as objects since in python they are just objects
        for objType in filter_interfaces(schema_types):
            obj = Object(objType)
            out.write(obj.toPython(py36plus=py36plus))

        # Pull objects and make them python objects
        for objType in filter_objects(schema_types):
            obj = Object(objType)
            out.write(obj.toPython(py36plus=py36plus))

        # Pull input objects and make them python objects
        for objType in filter_input_objects(schema_types):
            obj = InputObject(objType)
            out.write(obj.toPython(py36plus=py36plus))

        # lastly pull the unions and define TypeVars for them
        for union in filter_unions(schema_types):
            obj = Union(union)
            out.write(obj.toPython(py36plus=py36plus))

        out.write('\n')
        out.write('\n')

        # Pull the Query object and generate the API object
        query = Query(schema.get("queryType"))
        out.write(query.toPython(py36plus=py36plus))

        out.write('\n')
        out.write('\n')

        mutation = Mutation(schema.get("mutationType"))
        out.write(mutation.toPython(py36plus=py36plus))

        # don't forget to flush
        out.flush()
