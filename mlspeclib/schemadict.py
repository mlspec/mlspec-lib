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

        dict.__setitem__(self, schema_enum, parsed_yaml)
