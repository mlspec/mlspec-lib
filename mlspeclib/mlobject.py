# pylint: disable=attribute-defined-outside-init
""" Functions for loading and saving files to disk. """
import semver
from box import Box
import datetime
from pathlib import Path

import marshmallow.class_registry
from marshmallow import ValidationError

from mlspeclib.io import IO
from mlspeclib.mlschema import MLSchema
from mlspeclib.mlschemaenums import MLSchemaTypes
from mlspeclib.helpers import (
    check_and_return_schema_type_by_string,
    recursive_fromkeys,
    convert_yaml_to_dict,
    return_schema_name,
    to_yaml as helpers_to_yaml,
    to_json as helpers_to_json,
)


class Printable_Field:
    printable_name = None
    required = False
    field_type = None
    description = None
    constraint = None

    def __init__(
        self,
        printable_name: str,
        field_type,
        required: bool = False,
        description: str = None,
        constraint: str = None,
    ):
        self.printable_name = printable_name
        self.required = required
        self.field_type = field_type
        self.description = description
        self.constraint = constraint


class MLObject(Box):
    """ Contains all the fields loaded from an MLSpec, and validated against the MLSchema. Also
    provides load and save functions."""

    __version='0.0.1'

    def set_type(self, schema_version, schema_type, schema=None, schema_object=None):
        """ Used primarily after MLObject instantiation to set the schema_version and
        schema_type. Does verification of both fields and then loads a stub object
        with all fields set to 'None' except schema_version and schema_type."""

        try:
            semver.VersionInfo.parse(schema_version)
            self.__schema_version = schema_version
        except ValueError:
            raise ValueError(f"'{schema_version}' is not a valid semantic version.")
        except TypeError:
            raise ValueError(f"'{schema_version}' is not a valid semantic version.")

        self.__schema_type = check_and_return_schema_type_by_string(schema_type)
        self.__schema = schema
        self.__schema_object = schema_object

        self.create_stub_object()
        self.schema_version = self.get_schema_version()
        self.schema_type = self.get_schema_type().name.lower()

    def set_semver_and_type(
        self,
        schema_version=None,
        schema_type: MLSchemaTypes = None,
        contents_as_dict=None,
    ):
        """ Mostly internal function used to set variables for version and type. Should only \
            use rarely - if you use this separate from loading an object, you can get out \
            of sync."""

        if (schema_version is not None and schema_type is not None) and (
            contents_as_dict is not None
        ):
            raise Warning(
                "Semantic version + schema type and a dictionary were \
                           provided as the version & schema type, defaulting to \
                           using the content from the dictionary."
            )

        if contents_as_dict is not None:
            try:
                schema_version = contents_as_dict["schema_version"]
            except KeyError:
                raise KeyError(
                    "No field named 'schema_version' found at the top level of data."
                )

            try:
                schema_type = contents_as_dict["schema_type"]
            except KeyError:
                raise KeyError(
                    "No field named 'schema_type' found at the top level of data."
                )

    def create_stub_object(self):
        """ Creates a stub dictionary based on the schema with all values set to None.
        We do this because our goal is to prevent (eventually) creation of new attributes
        directly by users - only allowing them to use what we already provide to them
        to keep the schema in sync with the object."""

        MLSchema.populate_registry()
        version_number = self.get_schema_version()
        self.__schema_name = return_schema_name(
            version_number, self.get_schema_type().name
        )
        object_schema = marshmallow.class_registry.get_class(self.get_schema_name())
        self.__schema = object_schema()
        self.__schema_object = None
        these_fields = object_schema().fields
        this_key_dict = recursive_fromkeys(these_fields)
        self.merge_update(this_key_dict)

    def validate(self):
        """ Returns an array of errors after validating against the assigned
        schema. Each error is an array with the message at the 0-th index."""
        return self.get_schema().validate(self.dict_without_internal_variables())

    def save(self, save_path: Path, export_json=False):
        """ Copies all internal data to an MLSchema, which it then
        uses to validate, and saves to disk. Returns True on success,
        or False and an array of errors if it fails schema validation. """
        errors = self.validate()

        file_write_success = False
        if len(errors) == 0:
            file_path = save_path / (
                self.get_schema_name()
                + "-"
                + datetime.datetime.now().isoformat()
                + ".yaml"
            )

            export_dict = self.dict_without_internal_variables()
            if not export_json:
                IO.write_content_to_path(file_path, export_dict)
            else:
                IO.write_content_to_path(file_path, export_dict)

            # Expecting the file system to throw an error if something went wrong above.
            # By this point, the file system has written and so recording the filename.
            self.__file_path = file_path
            file_write_success = True
        return (file_write_success, errors)

    def to_yaml(self):
        return helpers_to_yaml(self.dict_without_internal_variables())

    def to_json(self):
        return helpers_to_json(self.dict_without_internal_variables())

    @staticmethod
    def code_gen(
        schema_version, schema_type, type_hints=True, prefix=None, only_required=False
    ) -> None:
        print(
            MLObject._code_gen_string(
                schema_version,
                schema_type,
                prefix=prefix,
                only_required=False,
                type_hints=type_hints,
            )
        )

    @staticmethod
    def _code_gen_string(
        schema_version, schema_type, prefix=None, only_required=False, type_hints=True
    ) -> str:
        stub_object = MLObject()
        stub_object.set_type(schema_version=schema_version, schema_type=schema_type)
        if prefix is None:
            prefix = "VARIABLE_NAME"
        all_objects = MLObject._build_all_printable_objects(
            stub_object.get_schema()._declared_fields, prefix
        )

        required_string = ""
        optional_string = ""

        for printable_object in all_objects:
            if printable_object.required:
                required_string += MLObject._string_for_field(
                    printable_object, type_hints
                )
            else:
                optional_string += MLObject._string_for_field(
                    printable_object, type_hints
                )

        complete_string = f"""

{prefix} = MLObject()
{prefix}.set_type('{schema_version}', '{stub_object.get_schema_type().name.lower()}')

#
# All required attributes
#
{required_string}

#
# All optional attributes
#
{optional_string}"""

        return complete_string

    @staticmethod
    def _string_for_field(printable_object: Printable_Field, type_hints=True) -> str:
        description_string = ""
        if printable_object.description is not None:
            description_string = f"""# {printable_object.description}
"""
        type_hint_string = ""
        if type_hints:
            type_hint_string = f"""\n# {printable_object.printable_name} expects -> {printable_object.field_type}
"""
            if printable_object.constraint is not None:
                type_hint_string += f"\n# Constraint: {printable_object.constraint}"

        assignment_string = f"""{printable_object.printable_name} =
"""
        return f"{description_string}{type_hint_string}{assignment_string}" ""

    @staticmethod
    def _build_all_printable_objects(fields_dict: dict, prefix: str) -> []:
        return_array = []
        for key in fields_dict:
            if key == "schema_version" or key == "schema_type":
                continue

            field = fields_dict[key]

            if hasattr(field, "nested"):
                return_array.extend(
                    MLObject._build_all_printable_objects(
                        field.schema._declared_fields, f"{prefix}.{key}"
                    )
                )
            else:
                description = None
                if hasattr(field, "description"):
                    description = field.description

                constraint = None
                if hasattr(field, "constraint"):
                    constraint = field.constraint

                return_array.append(
                    Printable_Field(
                        printable_name=f"{prefix}.{key}",
                        required=field.required,
                        field_type=type(field).__name__,
                        description=description,
                        constraint=constraint,
                    )
                )
        return return_array

    @staticmethod
    def create_object_from_file(file_path: str):
        """ Creates an MLObject based on a file path. File must be valid yaml."""
        ml_content_from_disk = IO.get_content_from_path(file_path)
        return MLObject.create_object_from_string(ml_content_from_disk)

    @staticmethod
    def create_object_from_string(file_contents):
        """ Creates an MLObject based on a string. String must be valid yaml.
        Returns Tuple MLObject and list of errors."""
        if(isinstance(file_contents, dict)):
            contents_as_dict = file_contents
        else:
            contents_as_dict = convert_yaml_to_dict(file_contents)

        # if (self.schema_type() is not None and self.version() is not None):
        #     schema_string = self.schema_type().name.lower()
        #     if (self.version() != contents_as_dict['schema_version'] or \
        #         schema_string != contents_as_dict['schema_type']):
        #         raise AttributeError("""The schema version and schema type were not in sync
        #     with those provided in the data. Rather than guessing which you want to use, we
        #     are throwing this error:
        #     Version Expected: %s
        #     Version Provided: %s
        #     Schema Type Expected: %s
        #     Schema Type Provided: %s """ % (self.version(), contents_as_dict['schema_version'], \
        #                                 schema_string, contents_as_dict['schema_type']))

        ml_object = MLObject()
        ml_object.set_type(
            schema_version=contents_as_dict["schema_version"],
            schema_type=contents_as_dict["schema_type"],
        )
        MLObject.update_tree(ml_object, contents_as_dict)
        errors = ml_object.validate()

        if len(errors) > 0:
            return (None, errors)
        else:
            return (ml_object, {})

    @staticmethod
    def update_tree(object_to_update, content):
        """ Updates the box tree to the content provided, and does a validation at the end. """
        for key in object_to_update:
            if isinstance(object_to_update[key], Box) and key in content.keys():
                MLObject.update_tree(object_to_update[key], content[key])

        object_to_update.merge_update(content)
        return object_to_update

    def dict_without_internal_variables(self):
        """ Returns a dict of all values on MLObject minus any with the prefix '_MLObject'
        (which are only for internal use). This allows us to validate on the whole dict."""
        return {
            k: v for k, v in self.to_dict().items() if not k.startswith("_MLObject")
        }

    # Simple getter functions with a prefix so that it's unlikely to be hidden
    # by values in the schema.

    # pylint: disable=missing-function-docstring
    def get_schema_version(self):
        return self.__schema_version

    # pylint: disable=missing-function-docstring
    def get_schema_type(self):
        if isinstance(self.__schema_type, MLSchemaTypes):
            return self.__schema_type
        else:
            # TODO: The below grossness is because I don't feel like going around and removing all the
            # places where get_schema_type().name is used. If I did, I could remove almost everything
            # here.
            class Object(object):
                pass

            a = Object()
            a.name = self.__schema_type
            return a

    # pylint: disable=missing-function-docstring
    def get_schema(self):
        return self.__schema

    # pylint: disable=missing-function-docstring
    def get_schema_object(self):
        return self.__schema_object

    # pylint: disable=missing-function-docstring
    def get_schema_name(self):
        return self.__schema_name

    # pylint: disable=missing-function-docstring
    def get_file_path(self):
        return self.__file_path
