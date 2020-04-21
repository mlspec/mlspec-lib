# pylint: disable=protected-access,missing-function-docstring, missing-class-docstring,
# pylint: disable=missing-module-docstring, missing-class-docstring, invalid-name
# -*- coding: utf-8 -*-
import unittest

from pathlib import Path

from tests.sample_submissions import SampleSubmissions

from mlspeclib.mlschemaenums import MLSchemaTypes
from mlspeclib.mlobject import MLObject
from mlspeclib.mlschema import MLSchema


class test_mlobject(unittest.TestCase):  # pylint: disable=invalid-name
    """MLobject test cases."""
    def test_create_ml_object(self):
        ml_object = MLObject()
        ml_object.set_type('0.0.1', MLSchemaTypes.DATAPATH)

        self.assertIsNotNone(ml_object)
        self.assertTrue(ml_object.schema_version == '0.0.1')
        self.assertTrue(ml_object.schema_type == MLSchemaTypes.DATAPATH.name.lower())

    def test_create_bad_semver(self):
        with self.assertRaises(ValueError):
            ml_object = MLObject()
            ml_object.set_type(schema_version='0.0.x', schema_type=MLSchemaTypes.BASE)

        with self.assertRaises(ValueError):
            ml_object = MLObject()
            ml_object.set_type(schema_version=None, schema_type=MLSchemaTypes.BASE)

    def test_create_bad_schema_type(self):
        with self.assertRaises(KeyError):
            ml_object = MLObject()
            ml_object.set_type(schema_version='0.0.1', schema_type='foo')

    def test_create_stub_base_object(self):
        ml_object = MLObject()
        ml_object.set_type('0.0.1', MLSchemaTypes.BASE)
        self.assertIsNone(ml_object['run_date'])
        self.assertTrue(len(ml_object) == 10)

    def test_create_stub_nested_object(self):
        ml_object = MLObject()
        ml_object.set_type('0.0.1', MLSchemaTypes.DATAPATH)
        self.assertTrue(len(ml_object) == 13)
        self.assertIsNone(ml_object.run_date)
        self.assertTrue(len(ml_object.connection) == 3)
        self.assertIsNone(ml_object.connection.endpoint)

    def test_load_object_with_missing_field_from_variable(self):

        WRONG_DATAPATH = """
schema_version: 0.0.1
schema_type: datapath
run_id: 6a9a5931-1c1d-47cc-aaf3-ad8b03f70575
step_id: 0c98f080-4760-46be-b35f-7dbb5e2a88c2
run_date: 1970-01-01 00:00:00.00000
# data_store: I_am_a_datastore_name
storage_connection_type: AWS_BLOB
connection:
    # endpoint: S3://mybucket/puppy.jpg
    access_key_id: AKIAIOSFODNN7EXAMPLE
    secret_access_key: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"""

        ml_object, errors = MLObject.create_object_from_string(WRONG_DATAPATH)

        self.assertTrue(len(ml_object) == 13)
        self.assertTrue(len(errors) == 2)
        self.assertTrue(errors['data_store'][0] == 'Field may not be null.')
        self.assertTrue(errors['connection']['endpoint'][0] == 'Field may not be null.')

    def test_load_object_from_disk(self):
        MLSchema.populate_registry()
        file_path = Path('tests/data/0/0/1/datapath.yaml')
        ml_object, _ = MLObject.create_object_from_file(file_path)

        self.assertIsNotNone(ml_object.run_date)
        self.assertIsNotNone(ml_object.connection.endpoint)

    @unittest.skip("NYI")
    def test_save_object_to_disk(self):
        content = SampleSubmissions.FULL_SUBMISSIONS.DATAPATH
        ml_object = MLSchema.create_object(content)
        ml_object.data_store = None
        ml_object.connection.endpoint = 'http://newsite.com'

        # filepath = "Not Necessary"
        # Test failing save on validation
        # Test Saving
        # Test file exists

        # mock_write_text.return_value = True
        # mock_read_text.return_value = yaml.safe_dump(ml_object.dict_without_internal_variables())

        # ml_object.save(yaml.safe_dump(ml_object.dict_without_internal_variables()))


if __name__ == '__main__':
    unittest.main()
