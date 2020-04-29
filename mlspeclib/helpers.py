""" Helper files for all functions """

from io import StringIO
import yaml as YAML
import uuid
import ast

from mlspeclib.mlschemaenums import MLSchemaTypes
from mlspeclib.mlschemafields import MLSchemaFields

from marshmallow.fields import Field, ValidationError

ALLOWED_OPERATORS = ["<", "<=", ">", ">=", "==", "%", "<>", "!="]


def repr_uuid(dumper, uuid_obj):
    return YAML.ScalarNode("tag:yaml.org,2002:str", str(uuid_obj))


def convert_yaml_to_dict(value):
    """ Converts raw text to yaml using ruamel (put into a helper to ease
        converting to other libraries in the future) """

    if isinstance(value, dict):
        return value
    else:
        return YAML.safe_load(value)


def convert_dict_to_yaml(value):
    """ Converts dict to yaml using ruamel (put into a helper to ease
        converting to other libraries in the future) """
    if isinstance(value, str):
        return value

    # pylint: disable=line-too-long
    string_io_handle = StringIO()
    YAML.SafeDumper.add_representer(uuid.UUID, repr_uuid)
    YAML.safe_dump(value, string_io_handle)
    return string_io_handle.getvalue()


def merge_two_dicts(first_dict, second_dict):
    """ Merges two python dicts by making a copy of first then updating with second.
        Returns a copy. """

    return_dict = first_dict.copy()  # start with x's keys and values
    return_dict.update(
        second_dict
    )  # modifies z with y's keys and values & returns None
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
    """ Builds a new dict with no values in it. Works recursively, but only looks for objects \
        with the 'nested' attribute."""
    return_dict = {}
    for key in full_dict.keys():
        if hasattr(full_dict[key], "nested"):
            return_dict[key] = recursive_fromkeys(
                full_dict[key].nested._declared_fields
            )
        else:
            if isinstance(full_dict[key], dict):
                return_dict[key] = {}
            else:
                return_dict[key] = None

    return return_dict


def contains_minimum_fields_for_schema(schema_dict: dict) -> bool:
    return_val = True
    return_val &= "mlspec_schema_version" in schema_dict
    return_val &= "mlspec_base_type" in schema_dict
    return_val &= "mlspec_schema_type" in schema_dict
    return_val &= "schema_version" in schema_dict
    return_val &= "schema_type" in schema_dict

    # Check for the sub values after we've already done the basics
    if return_val:
        return_val &= "meta" in schema_dict["mlspec_schema_version"]
        return_val &= "meta" in schema_dict["mlspec_base_type"]
        return_val &= "meta" in schema_dict["mlspec_schema_type"]
    return return_val


def valid_comparison_operator(val):
    return val in ALLOWED_OPERATORS


def generate_lambda(user_submitted_string):
    # make a list of safe functions
    safe_list = ["math", "lambda"]

    # use the list to filter the local namespace
    safe_dict = dict([(k, locals().get(k, None)) for k in safe_list])

    all_args = set()

    try:
        node = ast.parse(user_submitted_string, mode="eval")
    except TypeError:
        raise ValidationError(f"No value was passed in as a function as a constraint.")
    except SyntaxError:
        raise ValidationError(
            f'No parsable lambda was detected. Try it yourself: `ast.parse({user_submitted_string}, mode="eval")`'
        )

    for elem in ast.walk(node):
        if isinstance(elem, ast.Name):
            all_args.update(str(elem.id))

    if len(all_args) > 1:
        raise ValidationError(
            f"Only one variable ('x') is supported in lambda constraints at this time. The following variables were detected: '{','.join(all_args)}'"
        )

    if len(all_args) == 0:
        raise ValidationError(
            f"No variables were detected in the lambda constraint: '{user_submitted_string}'"
        )

    if list(all_args)[0] != "x":
        raise ValidationError(
            f"Only the variable 'x' is supported at this time. The following variables were detected: '{','.join(all_args)}'"
        )

    lambda_string = f"lambda {','.join(all_args)}: {user_submitted_string}"
    return_lambda = eval(lambda_string, {"__builtins__": None}, safe_dict)
    if lambda_string is None:
        raise ValidationError(
            'Could not parse %s into a lambda with one variable. Test yourself by running this on the command line: \
            \'eval(%s, {"__builtins__": None}, %s'
            % user_submitted_string,
            lambda_string,
            str(safe_dict),
        )
    else:
        return return_lambda


# def convert_marshmallow_field_to_primitive(marshmallow_field: Field):
#     field_name = type(marshmallow_field).__name__
#     try:
#         return MLSchemaFields.ALL_FIELD_TYPES[field_name]
#     except KeyError:
#         raise KeyError(f"'{field_name}' is not a known field type for code generation.")
