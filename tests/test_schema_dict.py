# pylint: disable=protected-access,missing-function-docstring, missing-class-docstring, missing-module-docstring
# -*- coding: utf-8 -*-
import unittest

from ruamel.yaml.scanner import ScannerError

from mlspeclib.helpers import convert_to_yaml
from mlspeclib.schemaenums import SchemaTypes
from mlspeclib.schemadict import SchemaDict
from mlspeclib.metadatavalidator import MetadataValidator
from tests.sample_schemas import SampleSchema

class SchemaDictTestSuite(unittest.TestCase):
    """SchemaDict test cases."""

    def test_enter_schema_with_valid_enum(self):
        schema_dict = SchemaDict()
        schema_dict[SchemaTypes.BASE] = SampleSchema.SCHEMAS.BASE
        assert len(schema_dict) == 1

    def test_enter_schema_with_invalid_enum(self):
        schema_dict = SchemaDict()
        with self.assertRaises(KeyError) as context:
            schema_dict['xxxx'] = SampleSchema.SCHEMAS.BASE

        self.assertTrue("is not an enum from mlspeclib.schemacatalog.SchemaTypes"\
                                                            in str(context.exception))

    def test_entering_string_and_converting_to_yaml(self):
        schema_dict = SchemaDict()
        schema_dict[SchemaTypes.BASE] = SampleSchema.SCHEMAS.BASE
        self.assertIsInstance(schema_dict[SchemaTypes.BASE], dict)
        self.assertTrue(schema_dict[SchemaTypes.BASE]['schema_version']['type'] == 'semver')

    def test_entering_yaml_and_not_converting(self):
        schema_dict = SchemaDict()
        schema_dict[SchemaTypes.BASE] = SampleSchema.SCHEMAS.BASE
        self.assertIsInstance(schema_dict[SchemaTypes.BASE], dict)
        self.assertTrue(schema_dict[SchemaTypes.BASE]['schema_version']['type'] == 'semver')

    def test_enter_schema_with_invalid_yaml(self):
        schema_dict = SchemaDict()

        with self.assertRaises(ScannerError):
            schema_dict[SchemaTypes.BASE] = SampleSchema.TEST.INVALID_YAML

    def test_test_valid_schema_with_invalid_yaml_submission(self):
        schema_dict = SchemaDict()
        schema_dict[SchemaTypes.BASE] = SampleSchema.SCHEMAS.BASE

        metadata_validator = MetadataValidator()

        with self.assertRaises(ScannerError):
            metadata_validator.validate(convert_to_yaml(\
                        SampleSchema.TEST.INVALID_YAML), schema_dict[SchemaTypes.BASE])

    def test_merge_two_dicts_with_invalid_base(self):
        schema_dict = SchemaDict()

        # Should not work - trying to instantiate a schema with a base_type
        # but the base_type has not been registered
        with self.assertRaises(KeyError) as context:
            schema_dict[SchemaTypes.DATAPATH] = SampleSchema.SCHEMAS.DATAPATH

        self.assertTrue("has not been registered as a schema and " \
                            "cannot be used as a base schema." in str(context.exception))

    def test_merge_two_dicts_with_valid_base(self):
        schema_dict = SchemaDict()

        schema_dict[SchemaTypes.BASE] = SampleSchema.SCHEMAS.BASE
        schema_dict[SchemaTypes.DATAPATH] = SampleSchema.SCHEMAS.DATAPATH

        # Should not work - BASE did not merge with DATAPATH
        with self.assertRaises(KeyError):
            schema_dict[SchemaTypes.BASE]['data_store'] == 'NULL_STRING_SHOULD_NOT_WORK' #pylint: disable=pointless-statement

        self.assertTrue(schema_dict[SchemaTypes.BASE]['run_id']['type'] == 'uuid')

        # Should work - DATAPATH inherited from BASE
        self.assertTrue(schema_dict[SchemaTypes.DATAPATH]['data_store']['type'] == 'string')
        self.assertTrue(schema_dict[SchemaTypes.DATAPATH]['run_id']['type'] == 'uuid')

if __name__ == '__main__':
    unittest.main()