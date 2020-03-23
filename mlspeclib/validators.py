import re
import uuid
import semver as sv
import uuid

class Validators:
    def __init__(self):
        pass

    def enum(self, Enum_Types, entry):
        try:
            return Enum_Types[entry]
        except KeyError:
            return False

    def semver(self, entry):
        try:
            return sv.parse(entry)
        except ValueError:
            return False
    
    def uuid(self, entry):
        try:
            return uuid.UUID(entry)
        except ValueError:
            return False

    def datetime(self, entry):
        pass