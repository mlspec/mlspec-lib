# pylint: disable=protected-access,missing-function-docstring, missing-class-docstring, missing-module-docstring
# -*- coding: utf-8 -*-
import unittest

from mlspeclib.helpers import convert_yaml_to_dict
from mlspeclib.metadatavalidator import MetadataValidator
from mlspeclib.schemaenums import SchemaTypes
from mlspeclib.schemacatalog import SchemaCatalog

from tests.sample_schemas import SampleSchema
from tests.sample_submissions import SampleSubmissions

@unittest.skip("NYI")
class SchemaCatalogTestSuite(unittest.TestCase):
    """SchemaCatalog test cases."""

    def test_add_schema_to_schemacatalog(self):
        semantic_version = '0.0.1'
        schema_type = SchemaTypes.BASE
        schema_catalog = SchemaCatalog()
        schema_catalog[semantic_version][schema_type] = SampleSchema.SCHEMAS.BASE

        metadata_validator = MetadataValidator()
        metadata_validator.schema = schema_catalog[semantic_version][schema_type]
        assert len(schema_catalog) == 1

    def test_test_schema_against_schema_from_catalog(self):
        semantic_version = '0.0.1'
        schema_type = SchemaTypes.BASE
        schema_catalog = SchemaCatalog()
        schema_catalog[semantic_version][schema_type] = SampleSchema.SCHEMAS.BASE

        metadata_validator = MetadataValidator()
        metadata_validator.schema = schema_catalog[semantic_version][schema_type]
        self.assertTrue(metadata_validator.validate(convert_yaml_to_dict(SampleSubmissions.BASE)))

    def test_try_add_with_invalid_semver(self):
        schema_catalog = SchemaCatalog()
        with self.assertRaises(KeyError) as context:
            schema_catalog['0.0.x'][SchemaTypes.BASE] = SampleSchema.SCHEMAS.BASE

        self.assertTrue("is not a valid Semantic Version" in str(context.exception))
        assert len(schema_catalog) == 0

    def test_load_all_schemas(self):
        schema_catalog = SchemaCatalog()
        schema_catalog._load_all_schemas()
        self.assertIsInstance(schema_catalog, SchemaCatalog)
        self.assertTrue(len(schema_catalog) > 0)

    def test_enter_schema_with_valid_enum(self):
        base_schema = MLSchema.create(SampleSchema.SCHEMAS.BASE)
        assert len(base_schema) == 1

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

    def test_enter_schema_with_invalid_yaml(self):
        ml_schema = MLSchema()

        with self.assertRaises(ScannerError):
            ml_schema[SchemaTypes.BASE] = SampleSchema.TEST.INVALID_YAML

    def test_test_valid_schema_with_invalid_yaml_submission(self):
        ml_schema = MLSchema()
        ml_schema[SchemaTypes.BASE] = SampleSchema.SCHEMAS.BASE

        metadata_validator = MetadataValidator()

        with self.assertRaises(ScannerError):
            metadata_validator.validate(convert_yaml_to_dict(\
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

if __name__ == '__main__':
    unittest.main()
