# -*- coding: utf-8 -*-
""" Test cases for MLObjects """

import unittest

from mlspeclib.helpers import convert_to_yaml, check_and_return_schema_type_by_string

from mlspeclib.schemacatalog import SchemaCatalog
from mlspeclib.schemaenums import SchemaTypes
from mlspeclib.metadatavalidator import MetadataValidator
from mlspeclib.mlobjects import GenericMLObject

from tests.sample_submissions import SampleSubmissions

class BasicTestSuite(unittest.TestCase):
    """Basic test cases."""

    def test_instantiate_schema_catalog(self):
        """Test to instantiate a schema catalog"""
        schema_catalog = SchemaCatalog()
        self.assertIsInstance(schema_catalog, SchemaCatalog)

    def test_instantiate_loads_at_least_two_schemas(self):
        """Test to ensure the schema catalog loads two schemas
           (since there are >=2 in default data)"""
        schema_catalog = SchemaCatalog()
        schema_catalog.populate()
        self.assertTrue(len(schema_catalog['0.0.1']) >= 2)

    def test_load_base_type_submission(self):
        """Load a schema catalog and then test it against a sample base submission"""
        schema_catalog = SchemaCatalog()
        schema_catalog.populate()

        loaded_submission = convert_to_yaml(SampleSubmissions.BASE)

        # Even though I know what the type is, I'm intentionally going to try to figure it out.
        schema_type = check_and_return_schema_type_by_string(loaded_submission['schema_type'])
        semver = loaded_submission['schema_version']

        metadata_validator = MetadataValidator()
        self.assertTrue(metadata_validator.validate(loaded_submission,
                                                    schema_catalog[semver][schema_type]))

    def test_load_datapath_type_submission(self):
        """Load a schema catalog and then test it against a sample datatype submission
           which uses a base_type"""

        schema_catalog = SchemaCatalog()
        schema_catalog.populate()

        loaded_submission = convert_to_yaml(SampleSubmissions.DATAPATH)

        # Even though I know what the type is, I'm intentionally going to try to figure it out.
        schema_type = check_and_return_schema_type_by_string(loaded_submission['schema_type'])
        semver = loaded_submission['schema_version']

        metadata_validator = MetadataValidator()
        self.assertTrue(metadata_validator.validate(loaded_submission,
                                                    schema_catalog[semver][schema_type]))

    def test_instantiate_inherited_mlobject(self):
        """Inherit from generic ml object and instantiate a base object"""

        base_class_object = type('Base', (GenericMLObject,), {'schema_enum': SchemaTypes.BASE})
        instanted_object = base_class_object()

        self.assertIsInstance(instanted_object, base_class_object)
