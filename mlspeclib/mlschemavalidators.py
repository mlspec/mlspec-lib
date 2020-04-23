""" Functions for validating submissions """
from distutils import util
import uritools
import semver as sv
import re
from marshmallow import ValidationError


# pylint: disable=missing-class-docstring
class MLSchemaValidators:
    @staticmethod
    def validate_type_semver(value):
        """ Uses the semver library to validate Semantic Version. Returns True/False """
        return sv.VersionInfo.isvalid(value)

    # pylint: disable=invalid-name
    @staticmethod
    def validate_type_URI(value):
        """ Uses the distutils library to validate date time. Returns True/False """
        return uritools.isuri(value)

    @staticmethod
    def validate_type_path(value):
        """ Uses regex to validate the value is a path. Returns True/False """
        path_regex = re.compile("(^[a-z0-9\-._~%!$&'()*+,;=:@/]+$)")  # noqa
        return path_regex.match(value)

    @staticmethod
    def validate_type_bucket(value):
        """ Uses regex to validate the value is a path. Returns True/False """
        bucket_regex = re.compile("(?=^.{3,63}$)(?!^(\d+\.)+\d+$)(^(([a-z0-9]|[a-z0-9][a-z0-9\-]*[a-z0-9])\.)*([a-z0-9]|[a-z0-9][a-z0-9\-]*[a-z0-9])$)")  # noqa
        return bucket_regex.match(value)

    @staticmethod
    def validate_type_string_cast(value):
        """ Casts value to string and validates. Returns True/False """
        # print(value)
        return isinstance(str(value), str)

    @staticmethod
    def validate_bool_and_return_string(val):
        """ Takes bool or string and converts value to string, testing
        if the result is true or false, and then casts result back to a string.

        Throws ValueError if it cannot be parsed as True/False.
        """

        # Convert to string first because some yaml libraries cast to booleans
        # and some leave as strings and we want to support both
        putative_bool_as_string = str(val)
        try:
            validated_bool = util.strtobool(putative_bool_as_string)
        except ValueError:
            raise ValueError(f"'{val}' is not a boolean value.")

        # We need to convert to 'True' or 'False' so first we cast to bool,
        # then to string.
        return str(bool(validated_bool))

    @staticmethod
    def validate_type_interface(interface_object: dict):
        """ Takes a Kubeflow Component interface and returns True/False if valid.
            From here: https://www.kubeflow.org/docs/pipelines/reference/component-spec/#detailed-specification-componentspec # noqa
        """
        # Kubeflow types manually copied from here -
        # https://github.com/kubeflow/pipelines/blob/master/sdk/python/kfp/dsl/types.py
        # TODO: Code gen this list: https://github.com/kubeflow/pipelines/blob/master/sdk/python/kfp/components/_structures.py # noqa
        kubeflow_types = {
            "Integer": int,
            "String": str,
            "Float": float,
            "Bool": bool,
            "List": list,
            "Dict": dict,
            "GcsPath": None,
            "GCPPath": None,
            "GCRPath": None,
            "GCPRegion": None,
            "GCPProjectID": None,
            "LocalPath": None,
            "Dataset": None,
            "AzureSku": None}

        # The schema gives us a list of dicts, each of which only has one entry. So we have to do
        # this - could theoretically  support multiple entries per list item if it comes to that.

        if 'name' in interface_object:
            # This is for the following:
            #   input:
            #   - { name: foo, type: bar}
            # TODO: THIS IS SUPER BROKEN, IT WILL FAIL ON INTERFACES NAMED 'name'
            interface_dict = interface_object
        else:
            # This is for the following:
            #   input:
            #   - foo: { type: bar}
            key = next(iter(interface_object.keys()))
            interface_dict = interface_object[key]
            interface_dict['name'] = key

        if 'type' in interface_dict:
            # TODO: Let's raise this with KFP folks - I think type should be required.
            # if 'type' in interface_dict:
            #   raise ValidationError(f"No type given for interface.")

            if isinstance(interface_dict['type'], dict) and len(interface_dict['type'].keys()) == 1:
                interface_type = next(iter(interface_dict['type'].keys()))
            elif isinstance(interface_dict['type'], str):
                interface_type = interface_dict['type']
            else:
                raise ValidationError(f"{interface_dict['type']} is expected to be a string or a dict with one entry.") # noqa

            if interface_type not in kubeflow_types.keys():
                raise ValidationError(f"'{interface_type}' is not a known type for an interface. Types are case sensistive. Please see this link for known types: https://aka.ms/kfptypes.") # noqa
            elif 'default' in interface_dict \
                 and kubeflow_types[interface_type] is not None:
                try:
                    kubeflow_types[interface_type](interface_dict['default'])
                except (ValueError, TypeError):
                    raise ValidationError(f"'{interface_dict['default']}' is not a valid default type for this field, nor is it castable using the provided type. If you were expecting it to be a string, make sure it's quoted.") # noqa

        # print(f"dict: f'{interface_dict}'")
        # print(f"key: '{key}'\ndict: f'{interface_dict}'")

        if 'name' in interface_dict and not isinstance(interface_dict['name'], str):
                raise ValidationError(f"{interface_dict['name']} is not a valid string (if you were expecting it to be cast as a string make sure it's quoted.") # noqa

        if 'description' in interface_dict and not isinstance(interface_dict['description'], str):
                raise ValidationError(f"{interface_dict['description']} is not a valid string (if you were expecting it to be cast as a string make sure it's quoted.") # noqa

        return True
