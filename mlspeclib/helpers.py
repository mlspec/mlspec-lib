""" Helper files for all functions """

from ruamel.yaml import YAML

from marshmallow import fields

from mlspeclib.schemaenums import SchemaTypes

def convert_to_yaml(text):
    """ Converts raw text to yaml using ruamel (put into a helper to ease
        converting to other libraries in the future) """

    yaml = YAML(typ='safe')
    return yaml.load(text)

def merge_two_dicts(first_dict, second_dict):
    """ Merges two python dicts by making a copy of first then updating with second.
        Returns a copy. """

    return_dict = first_dict.copy()   # start with x's keys and values
    return_dict.update(second_dict)    # modifies z with y's keys and values & returns None
    return return_dict

def check_and_return_schema_type_by_string(val):
    """ Looks up string in mlspeclib.schemaenums and returns enum of type SchemaTypes """

    try:
        return SchemaTypes[val.upper()]
    except AttributeError:
        raise KeyError("'%s' is not an enum from mlspeclib.schemacatalog.SchemaTypes" % val)
    except KeyError:
        raise KeyError("'%s' is not an enum from mlspeclib.schemacatalog.SchemaTypes" % val)
