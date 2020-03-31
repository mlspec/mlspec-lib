from mlspeclib.helpers import merge_two_dicts

import sys
import cerberus
from cerberus import Validator
from enum import Enum, auto
from mlspeclib.schemaenums import SchemaTypes
from mlspeclib.helpers import check_and_return_schema_type_by_string
from mlspeclib.metadatavalidator import MetadataValidator

from ruamel.yaml import YAML
import strictyaml

import semver

class SchemaDict(dict):
    def __getitem__(self, schema_type):
        return dict.__getitem__(self, schema_type)

    def __setitem__(self, schema_type, value):
        yaml = YAML(typ='safe')

        if type(schema_type) is str:
            schema_enum = check_and_return_schema_type_by_string(schema_type)
        else:
            schema_enum = check_and_return_schema_type_by_string(schema_type.name)

        if type(value) is str:
            parsed_yaml = yaml.load(value)
        else:
            parsed_yaml = value

        # The below is incredibly gross code smell - ideally, there'd 
        # be a much better way to merge the base schema with the derivative ones
        # and that allowed for multiple layers of inheritance. Oh well.
        # TODO: Support multiple layer of inheritence

        # If the yaml has a base_type
        if 'base_type' in parsed_yaml:
            base_name = parsed_yaml['base_type']['meta']
            # TODO: Figure out a more elegant way to ensure that base schema has already been loaded
            parent_schema_enum = check_and_return_schema_type_by_string(base_name)

            try:
                base_yaml = dict.__getitem__(self, parent_schema_enum)
            except(KeyError):
                raise KeyError("'%s' has not been registered as a schema and cannot be used as a base schema." % base_name)

            parsed_yaml = merge_two_dicts(parsed_yaml, base_yaml)

        s = MetadataValidator()
        s.schema = parsed_yaml

        dict.__setitem__(self, schema_enum, parsed_yaml)
