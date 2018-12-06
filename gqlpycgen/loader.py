from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport


schema_load_gql = """
{
  __schema {
    types {
      name
      kind
      interfaces {
        name
      }
      enumValues {
        name
      }
      fields {
        name
        args {
          name
          type {
            name
            kind
            ofType {
              name
              kind
            }
          }
        }
        type {
          name
          kind
          ofType {
            name
            kind
            ofType {
              name
              kind
              ofType {
                name
                kind
              }
            }
          }
          interfaces {
            name
          }
          possibleTypes {
            name
            kind
          }
        }
      }
      inputFields {
        name
        type {
          name
          kind
          ofType {
            name
            kind
            ofType {
              name
              kind
              ofType {
                name
                kind
              }
            }
          }
          interfaces {
            name
          }
          possibleTypes {
            name
            kind
          }
        }
      }
      possibleTypes {
        name
        kind
      }
    }
    queryType {
      fields {
        name
        type {
          name
        }
        args {
          name
          defaultValue
          type {
            name
            kind
            inputFields {
              name
            }
          }
        }
      }
    }
  }
}
"""


def load_remote_schema(uri):
    client = Client(transport=RequestsHTTPTransport(uri, use_json=True))
    gql_query = gql(schema_load_gql)
    schema = client.execute(gql_query)
    return schema.get("__schema")
