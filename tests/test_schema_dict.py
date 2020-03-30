# -*- coding: utf-8 -*-
from .context import mlspeclib
from mlspeclib.helpers import convert_to_yaml

from mlspeclib.schemaenums import SchemaTypes
from tests.sample_schemas import SampleSchema
from mlspeclib.schemadict import SchemaDict
from mlspeclib.schemavalidator import SchemaValidator

from ruamel.yaml.scanner import ScannerError

import unittest

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

        self.assertTrue("is not an enum from mlspeclib.schemacatalog.SchemaTypes" in str(context.exception))

    def test_entering_string_and_converting_to_yaml(self):
        sd = SchemaDict()
        sd[SchemaTypes.BASE] = SampleSchema.SCHEMAS.BASE
        self.assertIsInstance(sd[SchemaTypes.BASE], dict)
        self.assertTrue(sd[SchemaTypes.BASE]['schema_version']['type'] == 'semver')

    def test_entering_yaml_and_not_converting(self):
        sd = SchemaDict()
        sd[SchemaTypes.BASE] = SampleSchema.SCHEMAS.BASE
        self.assertIsInstance(sd[SchemaTypes.BASE], dict)
        self.assertTrue(sd[SchemaTypes.BASE]['schema_version']['type'] == 'semver')

    def test_enter_schema_with_invalid_yaml(self):
        sd = SchemaDict()
        
        with self.assertRaises(ScannerError):
            sd[SchemaTypes.BASE] = SampleSchema.TEST.INVALID_YAML

    def test_test_valid_schema_with_invalid_yaml_submission(self):
        schema_dict = SchemaDict()
        schema_dict[SchemaTypes.BASE] = SampleSchema.SCHEMAS.BASE

        s = SchemaValidator()

        with self.assertRaises(ScannerError):
            s.validate(convert_to_yaml(SampleSchema.TEST.INVALID_YAML), schema_dict[SchemaTypes.BASE])

    def test_merge_two_dicts_with_invalid_base(self):
        sd = SchemaDict()

        # Should not work - trying to instantiate a schema with a base_type but the base_type has not been registered
        with self.assertRaises(KeyError) as context:
            sd[SchemaTypes.BASE] = SampleSchema.TEST.TWO_THAT_REFERENCES_ONE

        self.assertTrue("has not been registered already, and cannoct be used as a base schema." in str(context.exception))

    def test_merge_two_dicts_with_valid_base(self):
        sd = SchemaDict()

        sd[SchemaTypes.BASE] = SampleSchema.TEST.ONE
        sd[SchemaTypes.DATAPATH] = SampleSchema.TEST.TWO_THAT_REFERENCES_ONE

        # Should not work - BASE did not merge with DATATYPE
        with self.assertRaises(KeyError):
            sd[SchemaTypes.BASE]['foo'] == 1

        self.assertTrue(sd[SchemaTypes.BASE]['qaz'] == 'a')

        # Should work - DATATYPE inherited from BASE
        self.assertTrue(sd[SchemaTypes.DATAPATH]['qaz'] == 'a')
        self.assertTrue(sd[SchemaTypes.DATAPATH]['foo'] == 1)

if __name__ == '__main__':
    unittest.main()