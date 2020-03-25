import sys
import re
import uuid
import semver as sv
import uuid
import cerberus
from cerberus import Validator
import datetime

class SchemaValidator(Validator):
    def _validate_type_semver(self, value):
        try:
            sv.parse(value)
            return True
        except ValueError:
            # error(field, "Not a SemVer")
            return False
    
    def _validate_type_uuid(self, value):
        try:
            uuid.UUID(value)
            return True
        except ValueError:
            # error(field, "Not a UUID")
            return False

