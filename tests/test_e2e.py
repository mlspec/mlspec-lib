# pylint: disable=protected-access,missing-function-docstring, missing-class-docstring, missing-module-docstring, missing-class-docstring # noqa
# -*- coding: utf-8 -*-
import unittest
import tempfile
import datetime
import uuid
from pathlib import Path

from marshmallow import ValidationError, pprint
import marshmallow.class_registry

from mlspeclib.helpers import convert_yaml_to_dict

from mlspeclib.mlschema import MLSchema
from mlspeclib.mlschemaenums import MLSchemaTypes
from mlspeclib.mlobject import MLObject

from tests.sample_schemas import SampleSchema
from tests.sample_submissions import SampleSubmissions


class e2eTestSuite(unittest.TestCase):  # pylint: disable=invalid-name
    """e2e test cases."""

    default_registry = None

    def setUp(self):
        if e2eTestSuite.default_registry is None:
            e2eTestSuite.default_registry = marshmallow.class_registry._registry.copy()
        else:
            marshmallow.class_registry._registry = e2eTestSuite.default_registry.copy()

        self.test_dir = tempfile.TemporaryDirectory()

    def tearDown(self):
        # Close the file, the directory will be removed after the test
        pass

    def test_load_full_base_schema(self):
        instantiated_schema = MLSchema.create_schema(SampleSchema.SCHEMAS.BASE)
        submission_dict = convert_yaml_to_dict(SampleSubmissions.FULL_SUBMISSIONS.BASE)
        instantiated_object = instantiated_schema.load(submission_dict)
        assert (
            instantiated_object["run_date"].isoformat()
            == submission_dict["run_date"].isoformat()
        )

        submission_dict.pop("run_date", None)
        with self.assertRaises(ValidationError):
            instantiated_schema.load(submission_dict)

    def test_load_full_datapath_schema(self):
        MLSchema.create_schema(SampleSchema.SCHEMAS.BASE)
        instantiated_schema = MLSchema.create_schema(SampleSchema.SCHEMAS.DATAPATH)
        submission_dict = convert_yaml_to_dict(
            SampleSubmissions.FULL_SUBMISSIONS.DATAPATH
        )
        instantiated_object = instantiated_schema.load(submission_dict)
        assert (
            instantiated_object["run_date"].isoformat()
            == submission_dict["run_date"].isoformat()
        )
        assert (
            instantiated_object["connection"]["endpoint"]
            == submission_dict["connection"]["endpoint"]
        )

        submission_dict.pop("run_date", None)
        with self.assertRaises(ValidationError):
            instantiated_schema.load(submission_dict)

    def test_load_and_save_file(self):
        run_id = uuid.uuid4()

        save_path = Path(self.test_dir.name) / str(run_id)
        save_path.mkdir()

        datapath_object = MLObject()
        datapath_object.set_type("0.0.1", MLSchemaTypes.DATAPATH)

        datapath_object.run_id = run_id
        datapath_object.step_id = uuid.uuid4()
        datapath_object.run_date = datetime.datetime.now()
        datapath_object.data_store = None  # This is an intentional bug

        # This is an intentional bug (Should be AWS_BLOB)
        datapath_object.storage_connection_type = "AWS_BLOB_OBJECT"
        datapath_object.connection.endpoint = None  # Another intentional bug
        datapath_object.connection.access_key_id = "AKIAIOSFODNN7EXAMPLE"
        datapath_object.connection.secret_access_key = (
            "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
        )

        response, errors = datapath_object.save(save_path)

        self.assertFalse(response)
        self.assertTrue(len(errors) == 3)
        self.assertTrue(len(list(Path(save_path).glob("*"))) == 0)

        datapath_object.storage_connection_type = "AWS_BLOB"

        response, errors = datapath_object.save(save_path)

        self.assertFalse(response)
        self.assertTrue(len(errors) == 2)
        self.assertTrue(len(list(Path(save_path).glob("*"))) == 0)

        datapath_object.connection.endpoint = "http://s3.amazon.com/BUCKET"

        response, errors = datapath_object.save(save_path)

        self.assertFalse(response)
        self.assertTrue(len(errors) == 1)
        self.assertTrue(len(list(Path(save_path).glob("*"))) == 0)

        datapath_object.data_store = "BUCKET NAME"

        response, errors = datapath_object.save(save_path)

        self.assertTrue(response)
        self.assertTrue(len(errors) == 0)
        path = Path(save_path)
        all_files = list(path.glob("*"))
        self.assertTrue(len(all_files) == 1)

        ml_object, errors = MLObject.create_object_from_file(all_files[0])
        self.assertTrue(len(ml_object) == 13)
        self.assertTrue(len(errors) == 0)

        self.assertTrue(datapath_object.data_store == ml_object.data_store)
        self.assertTrue(
            datapath_object.storage_connection_type == ml_object.storage_connection_type
        )
        self.assertTrue(
            datapath_object.connection.endpoint == ml_object.connection.endpoint
        )

    def test_all_schemas(self):
        MLSchema.populate_registry()
        all_001_schemas = list(Path("mlspeclib").glob("schemas/0/0/1/*.yaml"))

        self.assertTrue(len(all_001_schemas) > 1)

        for schema in all_001_schemas:
            this_text = schema.read_text()
            loaded_schema = MLSchema.create_schema(this_text)
            self.assertIsNotNone(loaded_schema.schema_name)

    def test_all_data(self):
        MLSchema.populate_registry()
        all_data_files = list(Path("tests").glob("data/0/0/1/*.yaml"))

        self.assertTrue(len(all_data_files) > 1)

        for data_file in all_data_files:
            print(data_file)
            loaded_object, errors = MLObject.create_object_from_file(data_file)
            self.assertTrue(len(errors) == 0)
            self.assertIsNotNone(loaded_object.get_schema())

    def test_live_interface_samples(self):
        MLSchema.populate_registry()

        print("Testing Keras")
        loaded_object, errors = MLObject.create_object_from_string(
            SampleSubmissions.FULL_SUBMISSIONS.COMPONENT_KERAS
        )

        pprint(errors)
        self.assertTrue(len(errors) == 0)
        self.assertIsNotNone(loaded_object.get_schema())

        print("Testing IBM")
        loaded_object, errors = MLObject.create_object_from_string(
            SampleSubmissions.FULL_SUBMISSIONS.COMPONENT_IBM
        )

        pprint(errors)
        self.assertTrue(len(errors) == 0)
        self.assertIsNotNone(loaded_object.get_schema())

        print("Testing OpenVino")
        loaded_object, errors = MLObject.create_object_from_string(
            SampleSubmissions.FULL_SUBMISSIONS.COMPONENT_OPENVINO
        )

        pprint(errors)
        self.assertTrue(len(errors) == 0)
        self.assertIsNotNone(loaded_object.get_schema())


if __name__ == "__main__":
    unittest.main()
