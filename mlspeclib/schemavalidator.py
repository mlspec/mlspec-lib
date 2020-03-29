import sys
import re
import uuid
import semver as sv
import uuid
import cerberus
from cerberus import Validator
from dateutil.parser import parse as dtparse
import strictyaml
from ruamel.yaml import YAML

class SchemaValidator(Validator):
    def _validate_type_semver(self, value):
        return sv.VersionInfo.isvalid(value)
    
    def _validate_type_uuid(self, value):
        try:
            uuid.UUID(value)
            return True
        except ValueError:
            # error(field, "Not a UUID")
            return False

    def _validate_type_datetime(self, value):
        try:
            dtparse(value)
            return True
        except:
            # error(field, "Not a datetime")
            return False

    def convert_and_validate(self, schema_to_check_in_text, schema_from_catalog_in_yaml):
        strictyaml.load(schema_to_check_in_text)

        ruamel_yaml = YAML()
        parsed_proposed_yaml = ruamel_yaml.load(schema_to_check_in_text)

        self.validate(parsed_proposed_yaml, schema_from_catalog_in_yaml)