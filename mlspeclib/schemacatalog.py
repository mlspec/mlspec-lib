import sys
import cerberus
import collections
from cerberus import Validator
from enum import Enum, auto
import semver as SemVer

from mlspeclib.schemadict import SchemaDict

class SchemaCatalog(dict):
    def __getitem__(self, semver):
        if SemVer.VersionInfo.isvalid(semver):
            return dict.setdefault(self, semver, SchemaDict())

        else:
            raise KeyError("'%s' is not a valid Semantic Version." % semver)        

    def __setitem__(self, semver, value):
        # Execute the below just to ensure it's a parseable semver
        if semver.VersionInfo.isvalid("semver"):
            dict.__setitem__(self, semver, value)
        else:
            raise KeyError("'%s' is not a valid Semantic Version." % semver)