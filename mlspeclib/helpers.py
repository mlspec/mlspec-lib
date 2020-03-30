from ruamel.yaml import YAML

from mlspeclib.schemaenums import SchemaTypes

def convert_to_yaml(text):
    yaml = YAML(typ='safe')
    return yaml.load(text)

def merge_two_dicts(x, y):
    z = x.copy()   # start with x's keys and values
    z.update(y)    # modifies z with y's keys and values & returns None
    return z

def check_and_return_schema_type_by_string(val):
    try:
        return SchemaTypes[val.upper()]
    except AttributeError:
        raise KeyError("'%s' is not an enum from mlspeclib.schemacatalog.SchemaTypes" % val)       
    except KeyError:
        raise KeyError("'%s' is not an enum from mlspeclib.schemacatalog.SchemaTypes" % val)       
