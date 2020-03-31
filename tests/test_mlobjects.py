# -*- coding: utf-8 -*-

from .context import mlspeclib
from mlspeclib.helpers import convert_to_yaml

from mlspeclib.core import PopulateRegistry
from mlspeclib.schemacatalog import SchemaCatalog
from mlspeclib.metadatavalidator import MetadataValidator
from mlspeclib.mlobjects import MLObjects
from pathlib import Path

from tests.sample_schemas import SampleSchema
from tests.sample_submissions import SampleSubmissions

import unittest

class BasicTestSuite(unittest.TestCase):
    """Basic test cases."""

    def test_instantiate_schema_catalog(self):
        sc = SchemaCatalog()
        self.assertIsInstance(sc, SchemaCatalog)

    def test_instantiate_loads_at_least_two_schemas(self):
        sc = SchemaCatalog()
        sc.populate()
        self.assertTrue(len(sc['0.0.1']) >= 2)

    def test_load_base_type_submission(self):
        sc = SchemaCatalog()
        sc.populate()

        loaded_submission = convert_to_yaml(SampleSubmissions.BASE)

        # Even though I know what the type is, I'm intentionally going to try to figure it out.
        schema_type = loaded_submission['schema_type'].upper()
        semver = loaded_submission['schema_version']

        s = MetadataValidator()
        self.assertTrue(s.validate(loaded_submission, sc[semver][schema_type]))
