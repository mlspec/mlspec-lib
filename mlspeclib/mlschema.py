""" MLSchema object which stores the yaml for all schemas for a single version. """
import re
from distutils import util

from marshmallow import Schema, fields, RAISE, validate, pre_load
import marshmallow.class_registry

from mlspeclib.helpers import convert_yaml_to_dict, \
                              check_and_return_schema_type_by_string, \
                              merge_two_dicts, \
                              get_class_name
from mlspeclib.mlschemafields import MLSchemaFields
from mlspeclib.mlschemavalidators import MLSchemaValidators


class MLSchema(Schema):
    """ Top level object for creating schema. Creates and stores schemas in
    marshmallow.class_registry (including nested schemas), and those schemas
    are used to .load({dicts}) into objects, and do schema verification."""

    schema_name = None
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
    # https://github.com/marshmallow-code/marshmallow/issues/1555
    # https://github.com/drgrib/dotmap

#    @validates_schema
#    def validate_semver(self, data, **kwargs):
#       print("\ninside validate semver\n")

    #pylint: disable=unused-argument, protected-access
    @pre_load
    def pre_load_data(self, data, **kwargs):
        """ Pre_load accomplishes two things:
            - First it creates the schema_name according to a standard
            pattern (schema_version with '.' replaced with '_',
            then an '_' then the specific schema name.).

            This means a standard registered schema name will be "0_0_1_datapath".

            - Second, this function checks for any fields that are of type -
            fields.Nested() and, if so, it looks up the schemas for those fields, and
            converts the data in those fields into an object. We need to do this because
            marshmallow requires an object (not a dict) to be attached in order to do
            validation on nested fields."""

        # TODO: May be worth exploring if we could create a custom validation type that used
        # dicts, instead of subobjects, because that would simplify a LOT of this code.

        data = convert_yaml_to_dict(data)

        if hasattr(self, 'schema_name'):
            schema_name = self.schema_name
        elif 'schema_name' in data:
            schema_name = data['schema_name']
        elif 'schema_version' in data and 'schema_type' in data:
            schema_name = get_class_name(data['schema_version'], data['schema_type'])
        else:
            raise KeyError("Submitted data must have both a schema_version and schema_type")

        try:
            schema = marshmallow.class_registry.get_class(schema_name)
        except:
            raise AttributeError(f"{schema_name} is not a valid schema type.")

        data = MLSchema.check_for_nested_schemas_and_convert(schema, schema_name, data)
        return data

    #pylint: disable=unused-argument, protected-access
    @staticmethod
    def check_for_nested_schemas_and_convert(schema, schema_name, data):
        """ Takes an object schema and looks through each of the fields to find a nested schema.
        If one is found, uses a sub function to convert the dict to a schema. This allows
        Marshmallow to provide schema verification on the subschema, which it otherwise wouldn't
        if it was a dict."""

        # TODO: More deeply horrifically grossness. Bleeding through the protected class on the schema
        # as well as tying to the specific field lookup to figure out the schema. Gotta figure out a
        # better way.

        for field in data:
            if field in schema._declared_fields and \
               hasattr(schema._declared_fields[field], 'nested'):
                sub_schema_name = schema_name+"_"+field.lower()
                sub_schema = marshmallow.class_registry.get_class(sub_schema_name)
                data[field] = MLSchema.convert_dict_to_schema(sub_schema, sub_schema_name, data[field])
        return data

    #pylint: disable=unused-argument, protected-access
    @staticmethod
    def convert_dict_to_schema(schema, schema_name, data):
        dict_to_load = {}

        for field in data:
            if hasattr(schema._declared_fields[field], 'nested'):
                sub_schema_name = schema_name+"_"+field.lower()
                sub_schema = marshmallow.class_registry.get_class(sub_schema_name)
                dict_to_load[field] = MLSchema.convert_dict_to_schema(sub_schema, sub_schema_name, data[field])
            else:
                dict_to_load[field] = data[field]

        return schema().load(dict_to_load)

    #pylint: disable=unused-argument, protected-access
    @staticmethod
    def create(raw_string: dict, class_name: str = None):
        abstract_schema_type = MLSchema.create_schema_type(raw_string, class_name)
        return abstract_schema_type()

    # pylint: disable=no-member, protected-access
    @staticmethod
    def create_schema_type(raw_string: dict, schema_name: str = None):
        """ Creates a new schema from a string of yaml. inheriting from MLSchema.\
            Schema still needs to be instantiated before use.

            e.g. this_schema = MLSchema.create(raw_string)
                 schema = this_schema()
                 this_object = schema.load(object_submission_dict)
            """
        schema_as_dict = convert_yaml_to_dict(raw_string)
        schema_as_dict = MLSchema._augment_with_base_schema(schema_as_dict)

        if schema_name is None:
            schema_name = MLSchema.generate_class_name(schema_as_dict)

        fields_dict = {}

        for field in schema_as_dict:
            if 'type' in schema_as_dict[field] and \
                schema_as_dict[field]['type'].lower() == 'nested':

                nested_schema_type = MLSchema.create_schema_type(schema_as_dict[field]['schema'], schema_name+"_"+field.lower())
                fields_dict[field] = fields.Nested(nested_schema_type)
            else:
                field_method = MLSchema._field_method_from_dict( \
                                        field, schema_as_dict[field])
                if field_method:
                    fields_dict[field] = field_method

        abstract_schema = MLSchema.from_dict(fields_dict)
        if schema_name:
            marshmallow.class_registry.register(schema_name, \
                                                abstract_schema)
            abstract_schema.schema_name = schema_name
        return abstract_schema

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
            if 'meta' in field_dict:
                # The field is a meta field about the schema, so skip adding a method
                return None
            field_type = field_dict['type'].lower()
            field_declaration = field_types[field_type]
        except KeyError:
            raise AttributeError(
                f"MLSchema Library has no field type named '{field_type}''")

        # Need to put this first so that we can redeclare the field function. Tried
        # attaching the regex without using the fields.Str(validate=) format,
        # and it didn't seem to work.
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

    @staticmethod
    def _augment_with_base_schema(schema_dict: dict):
        # The below is incredibly gross code smell - ideally, there'd
        # be a much better way to merge the base schema with the derivative ones
        # and that allowed for multiple layers of inheritance. Oh well.
        # TODO: Support multiple layer of inheritence

        parsed_yaml = schema_dict

        # If the yaml has a base_type
        if 'base_type' in schema_dict:
            base_name = schema_dict['base_type']['meta']
            # TODO: Figure out a more elegant way to ensure that base schema has already been loaded
            parent_schema_enum = check_and_return_schema_type_by_string(base_name)

            try:
                base_yaml = {}
            except KeyError:
                #pylint: disable=line-too-long
                raise KeyError("""'%s' has not been registered as a schema and cannot be used as a base schema.""" % base_name)

            parsed_yaml = merge_two_dicts(parsed_yaml, base_yaml)

        return parsed_yaml

    @staticmethod
    def generate_class_name(all_fields, class_prefix: str = None):
        """ Generates class name based on the fields in the dict.
        Moved to a helper function to ensure consistency. """
        mlspec_schema_type_string = None
        mlspec_version_string = None

        if 'mlspec_schema_type' in all_fields:
            mlspec_schema_type_string = all_fields['mlspec_schema_type']['meta']

        if 'mlspec_version' in all_fields:
            mlspec_version_string = all_fields['mlspec_version']['meta']

        _class_name = get_class_name(mlspec_version_string, mlspec_schema_type_string)
        if class_prefix and _class_name:
            _class_name = class_prefix + "_" + _class_name

        return _class_name
