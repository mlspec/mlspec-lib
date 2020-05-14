""" MLSchema object which converts yaml into objects and applies validation rules. """

import re
import os
from distutils import util

from yaml.scanner import ScannerError
from pathlib import Path

from marshmallow import Schema, fields, RAISE, validate, pre_load, ValidationError
import marshmallow.class_registry
from marshmallow.class_registry import RegistryError

import mlspeclib
from mlspeclib.helpers import (
    convert_yaml_to_dict,
    merge_two_dicts,
    contains_minimum_fields_for_schema,
    valid_comparison_operator,
    generate_lambda,
    build_schema_name_for_schema,
    build_schema_name_for_object,
)
from mlspeclib.mlschemafields import MLSchemaFields
from mlspeclib.mlschemavalidators import MLSchemaValidators

from ast import literal_eval

import logging


class MLSchema(Schema):
    """ Top level object for creating schema. Creates and stores schemas in
    marshmallow.class_registry (including nested schemas), and those schemas
    are used to .load({dicts}) into objects, and do schema verification."""

    schema_name = None

    # pylint: disable=too-few-public-methods
    class Meta:
        """ Meta options for MLSchema. """

        datetimeformat = "iso"  # ISO 8601 format
        render_module = "yaml"
        register = True
        unknown = RAISE

    # TODO: Want to add a DotMap to the underlying dictionary to make even cleaner access -
    # https://github.com/marshmallow-code/marshmallow/issues/1555
    # https://github.com/drgrib/dotmap

    # Functions below here are used for building schemas.

    # pylint: disable=unused-argument, protected-access
    @staticmethod
    def create_schema(raw_string: dict, schema_name: str = None):
        """ Uses create_schema_type to create a schema, and then instantiates it for return. """
        abstract_schema_type = MLSchema.create_schema_type(raw_string, schema_name)
        return abstract_schema_type()

    # pylint: disable=no-member, protected-access
    @staticmethod
    def create_schema_type(raw_string: dict, schema_name: str = None):
        """ Creates a new schema from a string of yaml. inheriting from MLSchema.\
            Schema still needs to be instantiated before use.

            e.g. this_schema = MLSchema.create_schema(raw_string)
                 schema = this_schema()
                 this_object = schema.load(object_submission_dict)
            """
        schema_as_dict = convert_yaml_to_dict(raw_string)
        schema_as_dict = MLSchema._augment_with_base_schema(schema_as_dict)

        if schema_name is None:
            # schema_name = foo_foo("a", "b")
            schema_name = build_schema_name_for_schema(
                mlspec_schema_version=schema_as_dict["mlspec_schema_version"],
                mlspec_schema_type=schema_as_dict["mlspec_schema_type"],
            )

        fields_dict = {}

        for field in schema_as_dict:
            if "marshmallow.fields" in str(
                type(schema_as_dict[field])
            ) or "mlschemafields.MLSchemaFields" in str(type(schema_as_dict[field])):
                # In this case, the field has already been created an instantiated properly (because
                # it comes from a base schema registered in marshmallow.class_registry). We can skip
                # all of the below and just add it to the field dict. This includes nested fields.
                fields_dict[field] = schema_as_dict[field]
            elif schema_as_dict[field] is None:
                raise AttributeError(
                    f"""It appears at the field '{field}' the yaml/dict \
                    is not formatted with attributes. Could it be an indentation error?"""
                )
            elif (
                "type" in schema_as_dict[field]
                and schema_as_dict[field]["type"].lower() == "nested"
            ):

                nested_schema_type = MLSchema.create_schema_type(
                    schema_as_dict[field]["schema"], schema_name + "_" + field.lower()
                )
                nested_schema_type.name = field
                fields_dict[field] = fields.Nested(nested_schema_type)
            else:
                field_method = MLSchema._field_method_from_dict(
                    field, schema_as_dict[field]
                )
                if field_method:
                    fields_dict[field] = field_method

        abstract_schema = MLSchema.from_dict(fields_dict)
        if schema_name:
            marshmallow.class_registry.register(schema_name, abstract_schema)
            abstract_schema.schema_name = schema_name
        return abstract_schema

    @staticmethod
    def _field_method_from_dict(name: str, field_dict: dict):
        """ Takes the dict from a yaml schema and creates a field appropriate for Marshmallow.  """
        field_types = {
            "string": fields.Str(),
            "uuid": fields.UUID(),
            "uri": fields.Str(validate=MLSchemaValidators.validate_type_URI),
            "datetime": MLSchemaFields.DateTime(),
            "semver": fields.Str(validate=MLSchemaValidators.validate_type_semver),
            "allowed_schema_types": fields.Str(),
            "boolean": fields.Boolean(),
            "list": fields.List(fields.Raw()),
            "list_strings": fields.List(
                fields.Str(validate=MLSchemaValidators.validate_type_string_cast)
            ),
            "list_of_tensor_shapes": fields.List(
                fields.Tuple([fields.Str(), fields.List(fields.Int)])
            ),
            "list_interfaces": fields.List(
                fields.Dict(validate=MLSchemaValidators.validate_type_interfaces)
            ),
            "workflow_steps": fields.Dict(
                validate=MLSchemaValidators.validate_type_workflow_steps
            ),
            "tags": fields.List(fields.Tuple([fields.Str(), fields.Str()])),
            "path": fields.Str(validate=MLSchemaValidators.validate_type_path),
            "dict": fields.Dict(),
            "float": fields.Float(),
            "email": fields.Email(),
            "bucket": fields.Str(validate=MLSchemaValidators.validate_type_bucket),
            "int": fields.Int(),
        }

        try:
            if "meta" in field_dict:
                # The field is a meta field about the schema, so skip adding a method
                return None
            field_type = field_dict["type"].lower()
            field_declaration = field_types[field_type]
        except KeyError:
            raise AttributeError(
                f"MLSchema Library has no field type named '{field_type}''"
            )

        # Need to put this first so that we can redeclare the field function. Tried
        # attaching the regex without using the fields.Str(validate=) format,
        # and it didn't seem to work.
        if "regex" in field_dict:
            try:
                re.compile(field_dict["regex"])
            except re.error:
                raise AssertionError(
                    f"The regex ('{field_dict['regex']}') does not appear to be a valid regex."
                )

            field_declaration = fields.Str(
                validate=validate.Regexp(
                    field_dict["regex"], error=f"No match for in field: {name}"
                )
            )

        if "allowed" in field_dict:
            # TODO: This may be a bug in waiting - would prefer not to overwrite, but instead
            # just to add. Filed a bug with marshmallow to see.
            # TODO: Bug - cannot currently support with "list"
            field_declaration = fields.Str(
                validate=validate.OneOf(field_dict["allowed"])
            )

        if "constraint" in field_dict:
            # TODO: There's probably a better place for this - it's validating
            # the constraint on an int or float that it's actually in the correct form but
            # isn't changing anything else.
            if field_type not in ["int", "float"]:
                raise ValueError(
                    "Attempting to add a 'constraint' to a field that does not appear to be a 'float' or 'int'."
                )
            if field_type == "int":
                field_declaration = fields.Int(
                    validate=generate_lambda(field_dict["constraint"])
                )
            elif field_type == "float":
                field_declaration = fields.Float(
                    validate=generate_lambda(field_dict["constraint"])
                )
            else:
                raise ValueError("Don't know how you got here.")

        if "required" in field_dict and util.strtobool(
            MLSchemaValidators.validate_bool_and_return_string(field_dict["required"])
        ):
            field_declaration.required = True
        else:
            field_declaration.allow_none = True

        if "empty" in field_dict and util.strtobool(
            MLSchemaValidators.validate_bool_and_return_string(field_dict["empty"])
        ):
            field_declaration.allow_none = True

        return field_declaration

    @staticmethod
    def _augment_with_base_schema(schema_dict: dict):
        # The below is incredibly gross code smell - ideally, there'd
        # be a much better way to merge the base schema with the derivative ones
        # and that allowed for multiple layers of inheritance. Oh well.
        # TODO: Support multiple layer of inheritence

        base_name = None
        base_version = None

        # If the yaml has a base_type
        if (
            "mlspec_base_type" in schema_dict
            and schema_dict["mlspec_base_type"]["meta"] is not None
        ):
            base_type = schema_dict["mlspec_base_type"]
        else:
            # There is no base type, so just return the full schema.
            return schema_dict

        if "mlspec_schema_version" in schema_dict:
            base_version = schema_dict["mlspec_schema_version"]
        else:
            raise KeyError(
                "There is no mlschema version for this spec, so cannot look up the base schema."
            )  # noqa
        try:
            base_schema = marshmallow.class_registry.get_class(
                build_schema_name_for_schema(
                    mlspec_schema_version=base_version, mlspec_schema_type=base_type
                )
            )

        except RegistryError:
            raise RegistryError(
                f"""Could not find the base schema in the class registry. Values provided:
        base_name = '{base_name}'
        base_type = '{base_type}'
        schema_version = '{base_version}'"""
            )

        base_dict = base_schema().fields

        schema_dict = merge_two_dicts(schema_dict, base_dict)

        return schema_dict

    # Functions below here are used for loading objects

    # pylint: disable=unused-argument, protected-access
    @pre_load
    def pre_load_data(self, data, **kwargs):
        """ Pre_load accomplishes two things:
            - First it builds the schema_name according to a standard
            pattern (schema_version with '.' replaced with '_',
            then an '_' then the specific schema name.).

            This means a standard registered schema name will look like "0_0_1_datapath".

            It needs to build this standard schema name because we will use it to
            retrieve the schema from marshmallow.class_registry

            - Second, this function checks for any fields that are of type -
            fields.Nested() and, if so, it looks up the schemas for those fields, and
            converts the data in those fields into an object. We need to do this because
            marshmallow requires an object (not a dict) to be attached in order to do
            validation on nested fields."""

        # TODO: May be worth exploring if we could create a custom validation type that used
        # dicts, instead of subobjects, because that would simplify a LOT of this code.

        data = convert_yaml_to_dict(data)
        schema_name = build_schema_name_for_object(self, data)

        try:
            marshmallow.class_registry.get_class(schema_name)
        except AttributeError:
            raise AttributeError(f"{schema_name} is not a valid schema type.")

        return data

    @staticmethod
    def create_object(submission_text: str):
        """ Creates an object that can be read and written to. """
        submission_dict = convert_yaml_to_dict(submission_text)
        schema = MLSchema.load_schema_from_registry(data=submission_dict)
        return schema().load(submission_dict)

    @staticmethod
    def load_schema_from_registry(data: dict):
        """ Loads just the schema from marshmallow's class_registry using the
        data (schema_type and schema_version) loaded from the submission. """

        schema_name = build_schema_name_for_object(submission_data=data)
        return marshmallow.class_registry.get_class(schema_name)

    # Functions below here are for filling out the registry
    @staticmethod
    def populate_registry():
        """ Loads all the base schemas for the schema registry. """

        schemas_to_process = []
        no_base = []
        has_base = []
        last = []

        load_root = os.path.dirname(mlspeclib.__file__)
        # logging.debug(f"Registry load root: {load_root}")
        load_path = Path(load_root).glob("schemas/**/*.yaml")
        # logging.debug(f"Registry load path: {load_path}")
        load_list = list(load_path)
        # logging.debug(f"Registry load list: {load_list}")

        for schema_file in load_list:
            schema_text = schema_file.read_text('utf-8')
            schema_dict = convert_yaml_to_dict(schema_text)

            if "last" in schema_dict["mlspec_schema_type"]:
                last.append(schema_dict)
            elif "mlspec_base_type" not in schema_dict:
                no_base.append(schema_dict)
            else:
                has_base.append(schema_dict)

        schemas_to_process = no_base + has_base + last

        for loaded_schema in schemas_to_process:
            loaded_schema_name = build_schema_name_for_schema(
                mlspec_schema_type=loaded_schema["mlspec_schema_type"],
                mlspec_schema_version=loaded_schema["mlspec_schema_version"],
            )
            try:
                marshmallow.class_registry.get_class(loaded_schema_name)
            except RegistryError:
                MLSchema.create_schema(loaded_schema)

    @staticmethod
    def append_schema_to_registry(load_path: Path) -> bool:
        if not isinstance(load_path, Path):
            raise TypeError("Appending schemas to a registry expects a Path object.")

        all_found_files = list(load_path.glob("**/*.yaml"))

        if len(all_found_files) == 0:
            raise FileNotFoundError(
                f"No files ending in '.yaml' were found in the path '{load_path}'"
            )

        all_schemas = []
        files_with_errors = []

        no_base_schemas = []
        schemas_with_base = []
        last_schemas = []

        for putative_schema_file in all_found_files:
            this_text = putative_schema_file.read_text('utf-8')
            try:
                this_dict = convert_yaml_to_dict(this_text)
            except ScannerError as se:
                files_with_errors.append(
                    (
                        putative_schema_file.name,
                        f"Yaml could not be parsed. Error details: \n{str(se)}",
                    )
                )
                continue

            if not contains_minimum_fields_for_schema(this_dict):
                files_with_errors.append(
                    (
                        putative_schema_file.name,
                        f"""Does not contain all of the minimum schema necessary as top level fields - list includes: mlspec_schema_version, mlspec_schema_version.meta, mlspec_base_type, mlspec_base_type.meta, mlspec_schema_type, mlspec_schema_type.meta, schema_version and schema_type""",
                    )
                )
                continue

            if "last" in this_dict["mlspec_schema_type"]:
                last_schemas.append(this_dict)
            elif "mlspec_base_type" in this_dict:
                schemas_with_base.append(this_dict)
            else:
                no_base_schemas.append(this_dict)

        all_schemas = no_base_schemas + schemas_with_base + last_schemas

        if len(files_with_errors) > 0:
            error_string = ""
            for err in files_with_errors:
                error_string += f"{err[0]}: {err[1]}\n"

            print(error_string)
            return False

        for schema_dict in all_schemas:
            schema_name = build_schema_name_for_schema(
                mlspec_schema_type=schema_dict["mlspec_schema_type"],
                mlspec_schema_version=schema_dict["mlspec_schema_version"],
            )
            try:
                marshmallow.class_registry.get_class(schema_name)
            except RegistryError:
                MLSchema.create_schema(schema_dict)
