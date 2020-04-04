# pylint: disable=protected-access,missing-function-docstring, missing-class-docstring, missing-module-docstring
# -*- coding: utf-8 -*-
import unittest

from mlspeclib.mlschema import MLSchema
from mlspeclib.helpers import convert_to_yaml
from tests.sample_schemas import SampleSchema
from tests.sample_submissions import SampleSubmissions

class SchemaTestSuite(unittest.TestCase):
    """MLSchema test cases."""

    def test_create_valid_schema(self):
        instantiated_schema, yaml_submission = return_base_schema_and_submission()
        assert len(instantiated_schema.declared_fields) == 5

    def test_create_base_object(self):
        instantiated_schema, yaml_submission = return_base_schema_and_submission()
        instantiated_object = instantiated_schema(yaml_submission)
        assert instantiated_object['run_date'].isoformat() == '1970-01-01T00:00:00'

    def test_enter_schema_with_invalid_yaml(self):
        ml_schema = MLSchema()

        with self.assertRaises(ScannerError):
            ml_schema[SchemaTypes.BASE] = SampleSchema.TEST.INVALID_YAML

    def test_test_valid_schema_with_invalid_yaml_submission(self):
        ml_schema = MLSchema()
        ml_schema[SchemaTypes.BASE] = SampleSchema.SCHEMAS.BASE

        metadata_validator = MetadataValidator()

        with self.assertRaises(ScannerError):
            metadata_validator.validate(convert_to_yaml(\
                        SampleSchema.TEST.INVALID_YAML), ml_schema[SchemaTypes.BASE])

    def test_merge_two_dicts_with_invalid_base(self):
        ml_schema = MLSchema()

        # Should not work - trying to instantiate a schema with a base_type
        # but the base_type has not been registered
        with self.assertRaises(KeyError) as context:
            ml_schema[SchemaTypes.DATAPATH] = SampleSchema.SCHEMAS.DATAPATH

        self.assertTrue("has not been registered as a schema and " \
                            "cannot be used as a base schema." in str(context.exception))

    def test_merge_two_dicts_with_valid_base(self):
        ml_schema = MLSchema()

        ml_schema[SchemaTypes.BASE] = SampleSchema.SCHEMAS.BASE
        ml_schema[SchemaTypes.DATAPATH] = SampleSchema.SCHEMAS.DATAPATH

        # Should not work - BASE did not merge with DATAPATH
        with self.assertRaises(KeyError):
            ml_schema[SchemaTypes.BASE]['data_store'] == 'NULL_STRING_SHOULD_NOT_WORK' #pylint: disable=pointless-statement

        self.assertTrue(ml_schema[SchemaTypes.BASE]['run_id']['type'] == 'uuid')

        # Should work - DATAPATH inherited from BASE
        self.assertTrue(ml_schema[SchemaTypes.DATAPATH]['data_store']['type'] == 'string')
        self.assertTrue(ml_schema[SchemaTypes.DATAPATH]['run_id']['type'] == 'uuid')
    @unittest.skip("NYI")
    def test_create_schema_with_invalid_base(self):
        pass

"""
    def test_enter_schema_with_invalid_enum(self):
        ml_schema = MLSchema()
        with self.assertRaises(KeyError) as context:
            ml_schema['xxxx'] = SampleSchema.SCHEMAS.BASE

        self.assertTrue("is not an enum from mlspeclib.schemacatalog.SchemaTypes"\
                                                            in str(context.exception))

    def test_entering_string_and_converting_to_yaml(self):
        ml_schema = MLSchema()
        ml_schema[SchemaTypes.BASE] = SampleSchema.SCHEMAS.BASE
        self.assertIsInstance(ml_schema[SchemaTypes.BASE], dict)
        self.assertTrue(ml_schema[SchemaTypes.BASE]['schema_version']['type'] == 'semver')

    def test_entering_yaml_and_not_converting(self):
        ml_schema = MLSchema()
        ml_schema[SchemaTypes.BASE] = SampleSchema.SCHEMAS.BASE
        self.assertIsInstance(ml_schema[SchemaTypes.BASE], dict)
        self.assertTrue(ml_schema[SchemaTypes.BASE]['schema_version']['type'] == 'semver')

"""

def return_base_schema_and_submission():
    base_schema = MLSchema.create(SampleSchema.SCHEMAS.BASE)
    instantiated_schema = base_schema()
    yaml_submission = convert_to_yaml(SampleSubmissions.FULL_SUBMISSIONS.BASE)
    return instantiated_schema, yaml_submission

if __name__ == '__main__':
    unittest.main()
