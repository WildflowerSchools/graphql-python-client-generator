from gqlpycgen.client import Client

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
      name
      interfaces {
        name
      }
      fields {
        name
        isDeprecated
        deprecationReason
        description
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
        }
        args {
          name
          defaultValue
          description
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
          }
        }
      }
    }
    mutationType {
      name
      interfaces {
        name
      }
      fields {
        name
        isDeprecated
        deprecationReason
        description
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
        }
        args {
          name
          defaultValue
          description
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
          }
        }
      }
    }
  }
}
"""


def load_remote_schema(uri):
    client = Client(uri)
    schema = client.execute(schema_load_gql)
    return schema.get("__schema")
