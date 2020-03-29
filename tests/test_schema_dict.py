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
        schema_dict[SchemaTypes.BASE] = SampleSchema.FULL
        assert len(schema_dict) == 1

    def test_enter_schema_with_invalid_enum(self):
        schema_dict = SchemaDict()
        with self.assertRaises(KeyError) as context:
            schema_dict['xxxx'] = SampleSchema.FULL

        self.assertTrue("is not an enum from mlspeclib.schemacatalog.SchemaTypes" in str(context.exception))

    def test_entering_string_and_converting_to_yaml(self):
        sd = SchemaDict()
        sd[SchemaTypes.BASE] = SampleSchema.FULL
        self.assertIsInstance(sd[SchemaTypes.BASE], dict)
        self.assertTrue(sd[SchemaTypes.BASE]['schema_version']['type'] == 'semver')

    def test_entering_yaml_and_not_converting(self):
        sd = SchemaDict()
        sd[SchemaTypes.BASE] = SampleSchema.FULL
        self.assertIsInstance(sd[SchemaTypes.BASE], dict)
        self.assertTrue(sd[SchemaTypes.BASE]['schema_version']['type'] == 'semver')

    def test_enter_schema_with_invalid_yaml(self):
        sd = SchemaDict()

        INVALID_YAML = """
a:
    - b
    % c"""
        
        with self.assertRaises(ScannerError) as context:
            sd[SchemaTypes.BASE] = INVALID_YAML

    def test_test_valid_schema_with_invalid_yaml_submission(self):
        schema_dict = SchemaDict()
        schema_dict[SchemaTypes.BASE] = SampleSchema.FULL

        INVALID_YAML = """
a:
    - b
    % c"""

        s = SchemaValidator()

        with self.assertRaises(ScannerError) as context:
            s.validate(convert_to_yaml(INVALID_YAML), schema_dict[SchemaTypes.BASE][SampleSchema.FULL])

    def test_merge_two_dicts(self):
        a = """
foo: 1
bar: 2
base_type: base"""

        b = """
qaz: a
quz: b"""

        sd = SchemaDict()
        sd[SchemaTypes.BASE] = b
        sd[SchemaTypes.DATAPATH] = a

        with self.assertRaises(KeyError):
            sd[SchemaTypes.BASE]['foo'] == 1

        self.assertTrue(sd[SchemaTypes.BASE]['qaz'] == 'a')

        self.assertTrue(sd[SchemaTypes.DATAPATH]['qaz'] == 'a')
        self.assertTrue(sd[SchemaTypes.DATAPATH]['foo'] == 1)

if __name__ == '__main__':
    unittest.main()