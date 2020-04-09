""" Functions for loading and saving files to disk. """
import semver as SemVer
from box import Box

from pathlib import Path
import marshmallow.class_registry

from mlspeclib.mlschema import MLSchema
from mlspeclib.mlschemaenums import MLSchemaTypes
from mlspeclib.helpers import check_and_return_schema_type_by_string, \
                              recursive_fromkeys

class MLObject(Box):
    def set_semver_and_type(self, semantic_version, schema_type: MLSchemaTypes):
        try:
            SemVer.parse(semantic_version)
            self.__version = semantic_version
        except ValueError:
            raise ValueError(f"'{semantic_version}' is not a valid semantic version.")
        except TypeError:
            raise ValueError(f"'{semantic_version}' is not a valid semantic version.")

        self.__schema_type = check_and_return_schema_type_by_string(schema_type)
        self.create_stub_object()

    def create_stub_object(self):
        MLSchema.populate_registry()
        version_number = self.version()
        schema_name = MLSchema.return_schema_name(version_number, self.schema_type().name)
        object_schema = marshmallow.class_registry.get_class(schema_name)
        object_instantiated = object_schema()
        self.merge_update(recursive_fromkeys(object_instantiated.fields))

    def populate_object_from_field(self, file_path):
        pass

    def version(self):
        return self.__version

    def schema_type(self):
        return self.__schema_type
