""" Helper files for all functions """

from io import StringIO
import yaml as YAML
import json as JSON
import uuid
import ast

from mlspeclib.mlschemaenums import MLSchemaTypes
from mlspeclib.mlschemafields import MLSchemaFields

from marshmallow.fields import Field, ValidationError
from marshmallow.class_registry import RegistryError

import base64
import pickle

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


def check_and_return_schema_type_by_string(val):
    """ Looks up string in mlspeclib.mlschemaenums and returns enum of type SchemaTypes """

    return val

    # if isinstance(val, MLSchemaTypes):
    #     return val

    # try:
    #     return MLSchemaTypes[val.upper()]
    # except AttributeError:
    #     raise KeyError("'%s' is not an enum from MLSchemaTypes" % val)
    # except KeyError:
    #     raise KeyError("'%s' is not an enum from MLSchemaTypes" % val)


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
    # return_val &= "mlspec_base_type" in schema_dict
    return_val &= "mlspec_schema_type" in schema_dict
    return_val &= "schema_version" in schema_dict
    return_val &= "schema_type" in schema_dict

    # Check for the sub values after we've already done the basics
    if return_val:
        return_val &= "meta" in schema_dict["mlspec_schema_version"]
        # return_val &= "meta" in schema_dict["mlspec_base_type"]
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


# Functions below here are just helper functions for building names.
def build_schema_name_for_schema(
    mlspec_schema_version: str, mlspec_schema_type: str, schema_prefix: str = None
):
    """ Generates schema name based on the fields in the dict.
    Moved to a helper function to ensure consistency. """

    try:
        mlspec_schema_type_string = mlspec_schema_type["meta"]
    except KeyError:
        raise KeyError("No mlschema_schema_type provided.")

    try:
        mlspec_schema_version_string = mlspec_schema_version["meta"]
    except KeyError:
        raise KeyError("No mlschema_schema_version provided.")

    schema_name = return_schema_name(
        mlspec_schema_version_string, mlspec_schema_type_string, schema_prefix
    )

    return schema_name


def build_schema_name_for_object(
    schema_object: dict = None, submission_data: dict = None, schema_prefix: str = None,
):
    """ Retrieves a schema_name from either the schema_object or the submitted data. """

    if schema_object is None and submission_data is None:
        raise KeyError(f"Neither schema_object nor submission_data was provided.")

    if (schema_object is not None and hasattr(schema_object, "schema_name")) and (
        schema_object.schema_name is not None
    ):
        schema_name = schema_object.schema_name
    elif "schema_name" in submission_data:
        schema_name = submission_data["schema_name"]
    elif (
        "schema_type" in submission_data and "schema_version" in submission_data
    ) and (
        submission_data["schema_type"] is not None
        and submission_data["schema_version"] is not None
    ):
        schema_name = return_schema_name(
            submission_data["schema_version"],
            submission_data["schema_type"],
            schema_prefix,
        )
    else:
        raise KeyError(
            f"Not enough information submitted to build a schema \
                            name for submission to class_registry."
        )

    return schema_name


def return_schema_name(
    raw_schema_version_string: str,
    raw_schema_type_string: str,
    schema_prefix: str = None,
):
    """ Takes Schema Version and Schema Type and returns a transformed schema name.
    Optionally takes a schema prefix to attach to the front. """

    schema_version_string = raw_schema_version_string.replace("-", r"_").replace(
        ".", r"_"
    )
    schema_name = schema_version_string + "_" + raw_schema_type_string.lower()

    if schema_prefix and schema_name:
        schema_name = schema_prefix + "_" + schema_name

    return schema_name


def get_sub_schema_name(schema_name, field_name):
    return schema_name + "_" + field_name.lower()


def encode_raw_object_for_db(mlobject):
    # Converts object -> dict -> yaml -> base64
    dict_conversion = mlobject.dict_without_internal_variables()
    yaml_conversion = convert_dict_to_yaml(dict_conversion)
    encode_to_utf8_bytes = yaml_conversion.encode("utf-8")
    base64_encode = base64.urlsafe_b64encode(encode_to_utf8_bytes)
    final_encode_to_utf8 = str(base64_encode, "utf-8")
    return final_encode_to_utf8


def decode_raw_object_from_db(s: str):
    # Converts base64 -> yaml
    base64_decode = base64.urlsafe_b64decode(s)
    return base64_decode


def to_yaml(this_dict: dict):
    return YAML.dump(this_dict)


def to_json(this_dict: dict):
    return JSON.dump(this_dict)


# def convert_marshmallow_field_to_primitive(marshmallow_field: Field):
#     field_name = type(marshmallow_field).__name__
#     try:
#         return MLSchemaFields.ALL_FIELD_TYPES[field_name]
#     except KeyError:
#         raise KeyError(f"'{field_name}' is not a known field type for code generation.")
