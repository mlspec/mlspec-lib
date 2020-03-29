from mlspeclib.helpers import merge_two_dicts

import sys
import cerberus
from cerberus import Validator
from enum import Enum, auto
from mlspeclib.schemaenums import SchemaTypes

from ruamel.yaml import YAML
import strictyaml

import semver

class SchemaDict(dict):
    def __getitem__(self, schema_type):
        return dict.__getitem__(self, schema_type)

    def __setitem__(self, schema_type, value):
        yaml = YAML(typ='safe')
        try:
            schema_enum = SchemaTypes[schema_type.name]
        except AttributeError:
            raise KeyError("'%s' is not an enum from mlspeclib.schemacatalog.SchemaTypes" % schema_type)       
        except KeyError:
            raise KeyError("'%s' must come from the set of schema types in mlspeclib.schemacatalog.SchemaTypes" % schema_type)       

        if type(value) is str:
            parsed_yaml = yaml.load(value)
        else:
            parsed_yaml = value

        # The below is incredibly gross code smell - ideally, there'd 
        # be a much better way to merge the base schema with the derivative ones
        # and that allowed for multiple layers of inheritance. Oh well.
        # TODO: Support multiple layer of inheritence
        # TODO: Don't look for a singe string to swap out
        # TODO: Don't hard code against the string in BASE

        # If the yaml has a base_type
        if 'base_type' in parsed_yaml:
            # TODO: Figure out a more elegant way to ensure that base schema has already been loaded
            base_yaml = dict.__getitem__(self, SchemaTypes.BASE)
            parsed_yaml = merge_two_dicts(parsed_yaml, base_yaml)

        dict.__setitem__(self, schema_enum, parsed_yaml)
