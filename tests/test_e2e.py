# pylint: disable=protected-access,missing-function-docstring, missing-class-docstring, missing-module-docstring, missing-class-docstring
# -*- coding: utf-8 -*-
import unittest

from mlspeclib.helpers import convert_to_yaml

from mlspeclib.metadatavalidator import MetadataValidator
from mlspeclib.mlschema import MLSchema
from mlspeclib.schemaenums import SchemaTypes

from tests.sample_schemas import SampleSchema
from tests.sample_submissions import SampleSubmissions

class e2eTestSuite(unittest.TestCase): #pylint: disable=invalid-name
    """e2e test cases."""
    def test_instantiate_validator(self):
        metadata_validator = MetadataValidator()
        self.assertIsInstance(metadata_validator, MetadataValidator)

    def test_load_allowed_list_schema(self):
        metadata_validator = MetadataValidator()

        schema_text = """
            storage_connection_type:
                type: string
                allowed:
                    - 'AWS_BLOB' # AWS Blob"""

        # Ideally this would not be necessary - we'd be able to overload
        # the assignment to schema with a conversion.
        # TODO: Swap out the below with a conversion after assignment
        metadata_validator.schema = convert_to_yaml(schema_text)

        value_text = """
            storage_connection_type: AWS_BLOB
        """

        metadata_validator.validate(convert_to_yaml(value_text))
        assert len(metadata_validator.errors) == 0

    def test_load_uuid_field(self):
        metadata_validator = MetadataValidator()

        schema_text = """
            run_id:
                type: uuid
                required: true
            """

        metadata_validator.schema = convert_to_yaml(schema_text)

        metadata_validator.validate(convert_to_yaml("run_id: f4bd7cee-42f9-4f29-a21e-3f78a9bad121"))
        assert len(metadata_validator.errors) == 0

        # Below contains an 'x' in position 2
        metadata_validator.validate(convert_to_yaml("run_id: fxbd7cee-42f9-4f29-a21e-3f78a9bad121"))
        assert len(metadata_validator.errors) == 1

    def test_load_semver_field(self):
        metadata_validator = MetadataValidator()

        schema_text = """
            schema_version:
                type: semver
                required: true
            """
        metadata_validator.schema = convert_to_yaml(schema_text)

        metadata_validator.validate(convert_to_yaml("schema_version: 0.0.1"))
        assert len(metadata_validator.errors) == 0

        # Below contains an 'x' in position 2
        metadata_validator.validate(convert_to_yaml("schema_version: x.x.x"))
        assert len(metadata_validator.errors) == 1

    def test_load_datetime_field(self):
        metadata_validator = MetadataValidator()

        schema_text = """
            run_date:
                type: datetime
                required: true
            """
        metadata_validator.schema = convert_to_yaml(schema_text)


        metadata_validator.validate(convert_to_yaml("run_date: 2020-03-25 14:17:38.977105"))
        assert len(metadata_validator.errors) == 0

        metadata_validator.validate(convert_to_yaml("run_date: 2020-03-25 14:17:38"))
        assert len(metadata_validator.errors) == 0

        metadata_validator.validate(convert_to_yaml("run_date: 1970-01-01 00:00:00.00000"))
        assert len(metadata_validator.errors) == 0

        # Need to change normalizer (when I get feedback on this question:
        # https://stackoverflow.com/questions/60857523/using-custom-validation-for-built-in-types)
        metadata_validator.validate(convert_to_yaml("run_date: xxxxx"))
        assert len(metadata_validator.errors) == 1

    def test_load_full_base_schema(self):
        ml_schema = MLSchema()
        ml_schema[SchemaTypes.BASE] = SampleSchema.SCHEMAS.BASE

        metadata_validator = MetadataValidator()
        metadata_validator.schema = ml_schema[SchemaTypes.BASE]
        metadata_validator.validate(convert_to_yaml(SampleSubmissions.BASE))
        assert len(metadata_validator.errors) == 0

    def test_load_full_datapath_schema(self):
        ml_schema = MLSchema()
        ml_schema[SchemaTypes.BASE] = SampleSchema.SCHEMAS.BASE
        ml_schema[SchemaTypes.DATAPATH] = SampleSchema.SCHEMAS.DATAPATH

        metadata_validator = MetadataValidator()
        metadata_validator.schema = ml_schema[SchemaTypes.DATAPATH]
        metadata_validator.validate(convert_to_yaml(SampleSubmissions.DATAPATH))
        assert len(metadata_validator.errors) == 0

if __name__ == '__main__':
    unittest.main()
