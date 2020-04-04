""" MLSchema object which stores the yaml for all schemas for a single version. """
import re
from distutils import util

from marshmallow import Schema, fields, RAISE, validate, ValidationError

from mlspeclib.helpers import convert_to_yaml
from mlspeclib.mlschemafields import MLSchemaFields
from mlspeclib.mlschemavalidators import MLSchemaValidators


class MLSchema(Schema):
    """ MLSchema  and ensures that the index is a SchemaType as well
    as making sure the yaml submitted is both valid yaml and is valid according to
    MetadataValidator. It also merges a schema based on the base_type (but does
    not do multiple levels of inheritance)."""

    # pylint: disable=too-few-public-methods
    class Meta:
        """ Meta options for MLSchema. """
        datetimeformat = 'iso'  # ISO 8601 format
        render_module = 'yaml'
        register = True
        unknown = RAISE

    # TODO: Want to add a DotMap to the underlying dictionary to make even cleaner access -
    # https://github.com/drgrib/dotmap

#    @validates_schema
#    def validate_semver(self, data, **kwargs):
#       print("\ninside validate semver\n")

    @staticmethod
    def create(raw_string: dict):
        """ Creates a new schema from a string of yaml. inheriting from MLSchema.\
            Schema still needs to be instantiated before use.

            e.g. this_schema = MLSchema.create(raw_string)
                 schema = this_schema()
                 this_object = schema.load(object_submission_dict)
            """
        schema_as_yaml = convert_to_yaml(raw_string)
        fields_dict = {}

        for field in schema_as_yaml:
            # pprint(f'{field}: {type(schema_as_yaml[field])}')
            fields_dict[field] = MLSchema._field_method_from_dict(
                field, schema_as_yaml[field])

        return MLSchema.from_dict(fields_dict)

    @staticmethod
    def _field_method_from_dict(name: str, field_dict: dict):
        """ Takes the dict from a yaml schema and creates a field appropriate for Marshmallow.  """
        field_types = {
            'string': fields.Str(),
            'uuid': fields.UUID(),
            'uri': fields.Str(validate=MLSchemaValidators.validate_type_URI),
            'datetime': MLSchemaFields.DateTime(),
            'semver': fields.Str(validate=MLSchemaValidators.validate_type_semver),
            'allowed_schema_types': fields.Str()
        }

        try:
            field_type = field_dict['type'].lower()
            field_declaration = field_types[field_type]
        except KeyError:
            raise AttributeError(
                f"MLSchema Library has no field type named '{field_type}''")

        # Need to put this first so that we can redeclare the field function. Tried
        # attaching the regex without using the fields.Str(validate=) format, and it didn't seem to work.
        if 'regex' in field_dict:
            try:
                re.compile(field_dict['regex'])
            except re.error:
                raise AssertionError(
                    f"The regex ('{field_dict['regex']}') does not appear to be a valid regex.")

            field_declaration = fields.Str(validate=validate.Regexp(
                field_dict['regex'], error=f"No match for in field: {name}"))

        if 'required' in field_dict and util.strtobool( \
                MLSchemaValidators.validate_bool_and_return_string(field_dict['required'])):
            field_declaration.required = True

        if 'empty' in field_dict and util.strtobool( \
                MLSchemaValidators.validate_bool_and_return_string(field_dict['empty'])):
            field_declaration.allow_none = False

        return field_declaration
