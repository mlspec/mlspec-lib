# pylint: disable=protected-access,missing-function-docstring, missing-class-docstring, missing-module-docstring, missing-class-docstring # noqa
# -*- coding: utf-8 -*-
import unittest
import tempfile
from pathlib import Path

from mlspeclib.helpers import convert_yaml_to_dict

import marshmallow.class_registry

from mlspeclib.mlschema import MLSchema
from mlspeclib.mlobject import MLObject


class liveSchemaTestSuite(unittest.TestCase):  # pylint: disable=invalid-name
    """live schema test cases."""

    default_registry = None

    def setUp(self):
        if liveSchemaTestSuite.default_registry is None:
            liveSchemaTestSuite.default_registry = marshmallow.class_registry._registry.copy()
        else:
            marshmallow.class_registry._registry = liveSchemaTestSuite.default_registry.copy()

        self.test_dir = tempfile.TemporaryDirectory()

    def tearDown(self):
        # Close the file, the directory will be removed after the test
        pass

    def test_load_live_schemas(self):
        MLSchema.populate_registry()
        all_schema_paths = list(Path('mlspeclib').glob('schemas/**/*.yaml'))

        for schema_path in all_schema_paths:
            this_text = schema_path.read_text()
            this_dict = convert_yaml_to_dict(this_text)
            if this_dict['mlspec_schema_version']['meta'] == '0.0.1':
                continue
            print(schema_path)
            loaded_schema = MLSchema.create_schema(this_text)
            self.assertIsNotNone(loaded_schema.schema_name)

    def test_load_live_data(self):
        MLSchema.populate_registry()
        all_data_files = list(Path('tests').glob('data/**/*.yaml'))

        for data_file in all_data_files:
            this_text = data_file.read_text()
            this_dict = convert_yaml_to_dict(this_text)
            if this_dict['schema_version'] == '0.0.1':
                continue
            print(data_file)
            loaded_object, errors = MLObject.create_object_from_file(data_file)
            self.assertTrue(len(errors) == 0)
            self.assertIsNotNone(loaded_object.get_schema())


if __name__ == '__main__':
    unittest.main()
