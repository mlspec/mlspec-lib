""" MLSchema object which stores the yaml for all schemas for a single version. """
import re
from distutils import util

from marshmallow import Schema, fields, RAISE, validate, pre_load
import marshmallow.class_registry
from marshmallow.class_registry import RegistryError

from mlspeclib.helpers import convert_yaml_to_dict, \
                              merge_two_dicts
from mlspeclib.mlschemafields import MLSchemaFields
from mlspeclib.mlschemavalidators import MLSchemaValidators


class MLSchema(Schema):
    """ Top level object for creating schema. Creates and stores schemas in
    marshmallow.class_registry (including nested schemas), and those schemas
    are used to .load({dicts}) into objects, and do schema verification."""

    schema_name = None

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

# Functions below here are used for building schemas.

    #pylint: disable=unused-argument, protected-access
    @staticmethod
    def create(raw_string: dict, schema_name: str = None):
        """ Uses create_schema_type to create a schema, and then instantiates it for return. """
        abstract_schema_type = MLSchema.create_schema_type(raw_string, schema_name)
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
            schema_name = MLSchema.get_schema_name(None, schema_as_dict)

        fields_dict = {}

        for field in schema_as_dict:
            if "marshmallow.fields" in str(type(schema_as_dict[field])) or \
               "mlschemafields.MLSchemaFields" in str(type(schema_as_dict[field])) :
                # In this case, the field has already been created an instantiated properly (because
                # it comes from a base schema registered in marshmallow.class_registry). We can skip
                # all of the below and just add it to the field dict. This includes nested fields.
                fields_dict[field] = schema_as_dict[field]

            elif 'type' in schema_as_dict[field] and \
                schema_as_dict[field]['type'].lower() == 'nested':

                nested_schema_type = MLSchema.create_schema_type( \
                                                                schema_as_dict[field]['schema'], \
                                                                schema_name+"_"+field.lower())
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



        base_name = None
        base_version = None

        # If the yaml has a base_type
        if 'mlspec_base_type' in schema_dict:
            base_name = schema_dict['mlspec_base_type']
        else:
            # There is no base type, so just return the full schema.
            return schema_dict

        if 'mlspec_schema_version' in schema_dict:
            base_version = schema_dict['mlspec_schema_version']
        else:
            raise KeyError(f"There is no mlschema version for this spec, \
                             so cannot look up the base schema.")
        try:
            base_schema = marshmallow.class_registry.get_class( \
                MLSchema.build_schema_name_for_schema(base_name, base_version))
        except RegistryError:
            raise RegistryError(f"""Could not find the base schema in the class \
registry. Values provided:
base_name = '{base_name}'
schema_version = '{base_version}'""")

        base_dict = base_schema().fields

        schema_dict = merge_two_dicts(schema_dict, base_dict)

        return schema_dict

# Functions below here are used for loading objects

    #pylint: disable=unused-argument, protected-access
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
        schema_name = MLSchema.get_schema_name(self, data)

        try:
            schema = marshmallow.class_registry.get_class(schema_name)
        except:
            raise AttributeError(f"{schema_name} is not a valid schema type.")

        data = MLSchema.check_for_nested_schemas_and_convert_to_object(schema, schema_name, data)
        return data

    #pylint: disable=unused-argument, protected-access
    @staticmethod
    def check_for_nested_schemas_and_convert_to_object(schema, schema_name, data):
        """ Takes an object schema and looks through each of the fields to find a nested schema.
        If one is found, uses a sub function to convert that dict to a schema. This allows
        Marshmallow to provide schema verification on the subschema, which it otherwise wouldn't
        if it was just an untyped dict."""

        # TODO: More deeply horrifically grossness. Bleeding through the protected class on
        # the schema as well as tying to the specific field lookup to figure out the schema.
        # Gotta figure out a better way.

        for field in data:
            if field in schema._declared_fields and \
               hasattr(schema._declared_fields[field], 'nested'):
                sub_schema_name = MLSchema.get_sub_schema_name(schema_name, field)
                sub_schema = marshmallow.class_registry.get_class(sub_schema_name)
                data[field] = MLSchema.convert_dict_to_schema(sub_schema, \
                                                              sub_schema_name, \
                                                              data[field])
        return data

    #pylint: disable=unused-argument, protected-access
    @staticmethod
    def convert_dict_to_schema(schema, schema_name, data):
        """ When passed in a dict, need to walk the dict and look for any nested fields that
        need converting to objects, which this function does and then attaches to a dict.
        If the field is just a standard field, then attach it to the dict. At the end,
        it takes the schema in 'schema' and instantiates & loads the object.

        Need to pass in the schema_name because most sub_schemas won't have version or type
        information, and we need to use that to look up the schema from the class_registry."""

        dict_to_load = {}

        for field in data:
            if hasattr(schema._declared_fields[field], 'nested'):
                sub_schema_name = schema_name+"_"+field.lower()
                sub_schema = marshmallow.class_registry.get_class(sub_schema_name)
                dict_to_load[field] = MLSchema.convert_dict_to_schema(sub_schema, \
                                                                      sub_schema_name, \
                                                                      data[field])
            else:
                dict_to_load[field] = data[field]

        return schema().load(dict_to_load)

# Functions below here are just helper functions for building names.

    @staticmethod
    def get_schema_name(schema_object, data):
        """ Retrieves a schema_name from either the schema_object or the submitted data. """

        if hasattr(schema_object, 'schema_name') and schema_object.schema_name is not None:
            schema_name = schema_object.schema_name
        elif 'schema_name' in data:
            schema_name = data['schema_name']
        elif 'mlspec_schema_version' in data and 'mlspec_schema_type' in data:
            schema_name = MLSchema.build_schema_name_for_schema(data['mlspec_schema_type'], \
                                                                data['mlspec_schema_version'], \
                                                                None)
        else:
            raise KeyError(f"""Not enough information submitted to build a schema type.""")

        return schema_name

    @staticmethod
    def build_schema_name_for_schema(mlspec_schema_type: str, \
                                     mlspec_schema_version: str, \
                                     schema_prefix: str = None):
        """ Generates schema name based on the fields in the dict.
        Moved to a helper function to ensure consistency. """

        try:
            mlspec_schema_type_string = mlspec_schema_type['meta']
        except KeyError:
            raise KeyError("No mlschema_schema_type provided.")

        try:
            mlspec_schema_version_string = mlspec_schema_version['meta']
        except KeyError:
            raise KeyError("No mlschema_schema_version provided.")

        schema_name = MLSchema.return_schema_name(mlspec_schema_version_string, \
                                                  mlspec_schema_type_string, \
                                                  schema_prefix)

        return schema_name

    @staticmethod
    def build_schema_name_for_object(all_fields, schema_prefix: str = None):
        """ Generates schema name based on the fields in the dict.
        Moved to a helper function to ensure consistency. """
        schema_name = None

        if (all_fields['schema_type'] and all_fields['schema_version']):
            schema_name = MLSchema.return_schema_name(all_fields['schema_version'], \
                                                      all_fields['schema_type'], \
                                                      schema_prefix)

        return schema_name

    @staticmethod
    def return_schema_name(raw_schema_version_string: str, \
                           raw_schema_type_string: str, \
                           schema_prefix: str = None):
        """ Takes Schema Version and Schema Type and returns a transformed schema name.
        Optionally takes a schema prefix to attach to the front. """

        schema_version_string = raw_schema_version_string.replace('-', r'_').replace('.', r'_')
        schema_name = schema_version_string + "_" + raw_schema_type_string.lower()

        if schema_prefix and schema_name:
            schema_name = schema_prefix + "_" + schema_name

        return schema_name

    #pylint: disable=missing-function-docstring
    @staticmethod
    def get_sub_schema_name(schema_name, field_name):
        return schema_name + "_" + field_name.lower()
