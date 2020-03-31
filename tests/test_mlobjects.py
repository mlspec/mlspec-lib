# -*- coding: utf-8 -*-

from .context import mlspeclib
from mlspeclib.helpers import convert_to_yaml

from mlspeclib.core import PopulateRegistry
from mlspeclib.schemacatalog import SchemaCatalog
from mlspeclib.schemavalidator import SchemaValidator
from mlspeclib.mlobjects import MLObjects
from tests.sample_schemas import SampleSchema
from pathlib import Path

import unittest

class BasicTestSuite(unittest.TestCase):
    """Basic test cases."""

    @unittest.skip("Not Implemented Yet")
    def test_instantiate_types(self):
        sc = SchemaCatalog()
        self.assertIsInstance(sc, SchemaCatalog)
