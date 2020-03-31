import sys
import re
import uuid
import semver as sv

import validators
import uritools

import cerberus
from cerberus import Validator

from dateutil.parser import parse as dtparse

from mlspeclib.helpers import check_and_return_schema_type_by_string

import strictyaml
from ruamel.yaml import YAML

class MetadataValidator(Validator):
    def _validate_type_semver(self, value):
        return sv.VersionInfo.isvalid(value)
    
    def _validate_type_uuid(self, value):
        return validators.uuid(value)

    def _validate_type_datetime(self, value):
        try:
            dtparse(value)
            return True
        except:
            # error(field, "Not a datetime")
            return False

    def _validate_type_URI(self, value):
        return uritools.isuri(value)

    def _validate_type_metadata(self, value):
        return True

    def _validate_type_allowed_schema_types(self, value):
        return check_and_return_schema_type_by_string(value)

    def convert_and_validate(self, schema_to_check_in_text, schema_from_catalog_in_yaml):
        strictyaml.load(schema_to_check_in_text)

        ruamel_yaml = YAML()
        parsed_proposed_yaml = ruamel_yaml.load(schema_to_check_in_text)

        self.validate(parsed_proposed_yaml, schema_from_catalog_in_yaml)