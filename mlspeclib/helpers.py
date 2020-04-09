""" Helper files for all functions """

from ruamel.yaml import YAML

from mlspeclib.mlschemaenums import MLSchemaTypes

def convert_yaml_to_dict(value):
    """ Converts raw text to yaml using ruamel (put into a helper to ease
        converting to other libraries in the future) """

    if isinstance(value, dict):
        return value
    else:
        yaml = YAML(typ='safe')
        return yaml.load(value)

def merge_two_dicts(first_dict, second_dict):
    """ Merges two python dicts by making a copy of first then updating with second.
        Returns a copy. """

    return_dict = first_dict.copy()   # start with x's keys and values
    return_dict.update(second_dict)    # modifies z with y's keys and values & returns None
    return return_dict

def check_and_return_schema_type_by_string(val: MLSchemaTypes):
    """ Looks up string in mlspeclib.mlschemaenums and returns enum of type SchemaTypes """

    if isinstance(val, MLSchemaTypes):
        return val

    try:
        return MLSchemaTypes[val.upper()]
    except AttributeError:
        raise KeyError("'%s' is not an enum from MLSchemaTypes" % val)
    except KeyError:
        raise KeyError("'%s' is not an enum from MLSchemaTypes" % val)

def recursive_fromkeys(full_dict: dict):
    """ Builds a new dict with no values in it. Works recursively, but only looks for 'dict's."""
    return_dict = {}
    for key in full_dict.keys():
        if hasattr(full_dict[key], 'nested'):
            return_dict[key] = recursive_fromkeys(full_dict[key].nested._declared_fields)
        else:
            return_dict[key] = None

    return return_dict