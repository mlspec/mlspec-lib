import sys
import cerberus
import collections
from cerberus import Validator
from enum import Enum, auto
import semver as SemVer

from pathlib import Path

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

    def _load_all_schemas(self):
        # The below is extremely gross - fix
        all_schema_type_paths = list(Path("mlspeclib/data").rglob("*.yaml"))
        print (all_schema_type_paths)
        for schema_type_path in all_schema_type_paths:
            self._read_schema_type(schema_type_path)
        return self

    def _read_schema_type(self, f):
        print("Reading %s" % f)
        content = f.read_text()

        # TODO: Make this less ugly somehow - shouldn't hardcode the version by directory paths - oh well
        semver = '.'.join(f.parts[2:5])

        # TODO: Make this less ugly somehow - shouldn't hard code into the file name and, split and then upper
        schema_type = f.name.split('.')[0].upper()

        self[semver][schema_type] = content

        return self

    def populate(self):
        self._load_all_schemas()
        return self