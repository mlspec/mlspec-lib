# pylint: disable=protected-access,missing-function-docstring, missing-class-docstring, missing-module-docstring
# -*- coding: utf-8 -*-
import unittest

from mlspeclib.helpers import convert_to_yaml
from mlspeclib.metadatavalidator import MetadataValidator
from mlspeclib.schemaenums import SchemaTypes
from mlspeclib.schemacatalog import SchemaCatalog

from tests.sample_schemas import SampleSchema
from tests.sample_submissions import SampleSubmissions

class SchemaCatalogTestSuite(unittest.TestCase):
    """SchemaCatalog test cases."""

    def test_add_schemadict_to_schemacatalog(self):
        semantic_version = '0.0.1'
        schema_type = SchemaTypes.BASE
        schema_catalog = SchemaCatalog()
        schema_catalog[semantic_version][schema_type] = SampleSchema.SCHEMAS.BASE

        metadata_validator = MetadataValidator()
        metadata_validator.schema = schema_catalog[semantic_version][schema_type]
        assert len(schema_catalog) == 1

    def test_test_schema_against_schemadict_from_catalog(self):
        semantic_version = '0.0.1'
        schema_type = SchemaTypes.BASE
        schema_catalog = SchemaCatalog()
        schema_catalog[semantic_version][schema_type] = SampleSchema.SCHEMAS.BASE

        metadata_validator = MetadataValidator()
        metadata_validator.schema = schema_catalog[semantic_version][schema_type]
        self.assertTrue(metadata_validator.validate(convert_to_yaml(SampleSubmissions.BASE)))

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


if __name__ == '__main__':
    unittest.main()
