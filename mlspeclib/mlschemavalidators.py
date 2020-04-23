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
            From here: https://www.kubeflow.org/docs/pipelines/reference/component-spec/#detailed-specification-componentspec
        """

        # Kubeflow types manually copied from here -
        # https://github.com/kubeflow/pipelines/blob/master/sdk/python/kfp/dsl/types.py
        # TODO: Code gen this list: https://github.com/kubeflow/pipelines/blob/master/sdk/python/kfp/components/_structures.py
        kubeflow_types = {
            "Integer": int,
            "String": str,
            "Float": float,
            "Bool": bool,
            "List": list,
            "Dict": dict,
            "GCPPath": None,
            "GCRPath": None,
            "GCPRegion": None,
            "GCPProjectID": None,
            "LocalPath": None,
            "Dataset": None,
            "AzureSku": None}

        # The schema gives us a list of dicts, each of which only has one entry. So we have to do
        # this - could theoretically  support multiple entries per list item if it comes to that.
        for key in interface_object:
            interface_dict = interface_object[key]

            if 'type' not in interface_dict:
                raise ValidationError(f"No type given for interface.")
            elif interface_dict['type'] not in kubeflow_types.keys():
                raise ValidationError(f"'{interface_dict['type']}' is not a known type for an interface. Types are case sensistive. Please see this link for known types: https://aka.ms/kfptypes.") # noqa
            elif 'default' in interface_dict \
                and kubeflow_types[interface_dict['type']] is not None \
                and not isinstance(interface_dict['default'],
                                   kubeflow_types[interface_dict['type']]):
                raise ValidationError(f"'{interface_dict['default']}' is not a valid default type for this field. If you were expecting it to be a string, make sure it's quoted.") # noqa

            if 'name' in interface_dict:
                if not isinstance(interface_dict['name'], str):
                    raise ValidationError(f"{interface_dict['name']} is not a valid string (if you were expecting it to be cast as a string make sure it's quoted.") # noqa

            if 'description' in interface_dict:
                if not isinstance(interface_dict['description'], str):
                    raise ValidationError(f"{interface_dict['description']} is not a valid string (if you were expecting it to be cast as a string make sure it's quoted.") # noqa

        return True


# name: Human-readable name of the input/output. Name must be unique inside the inputs or outputs section, but an output may have the same name as an input.
# description: Human-readable description of the input/output.
# default: Specifies the default value for an input. Only valid for inputs.
# type: Specifies the type of input/output. The types are used as hints for pipeline authors and can be used by the pipeline system/UI to validate arguments and connections between components. Basic types are String, Integer, Float, and Bool. See the full list of types defined by the Kubeflow Pipelines SDK.
