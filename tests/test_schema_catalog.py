# -*- coding: utf-8 -*-
from .context import mlspeclib
from mlspeclib.helpers import convert_to_yaml


from mlspeclib.schemavalidator import SchemaValidator
from mlspeclib.schemaenums import SchemaTypes
from tests.sample_schemas import SampleSchema
from mlspeclib.schemadict import SchemaDict
from mlspeclib.schemacatalog import SchemaCatalog

import semver as SemVer
import unittest

class SchemaCatalogTestSuite(unittest.TestCase):
    """SchemaCatalog test cases."""

    def test_add_schemadict_to_schemacatalog(self):
        sv = '0.0.1'
        st = SchemaTypes.BASE
        schema_catalog = SchemaCatalog()
        schema_catalog[sv][st] = SampleSchema.FULL
        
        s = SchemaValidator()
        s.schema = schema_catalog[sv][st]
        assert len(schema_catalog) == 1

    def test_test_schema_against_schemadict_from_catalog(self):
        sv = '0.0.1'
        st = SchemaTypes.BASE
        schema_catalog = SchemaCatalog()
        schema_catalog[sv][st] = SampleSchema.FULL

        s = SchemaValidator()
        s.schema = schema_catalog[sv][st]
        self.assertTrue(s.validate(convert_to_yaml(SampleSchema.FULL_SUBMITTED)))

    def test_try_add_with_invalid_semver(self):
        schema_catalog = SchemaCatalog()
        with self.assertRaises(KeyError) as context:
            schema_catalog['0.0.x'][SchemaTypes.BASE] = SampleSchema.FULL

        self.assertTrue("is not a valid Semantic Version" in str(context.exception))
        assert len(schema_catalog) == 0


if __name__ == '__main__':
    unittest.main()