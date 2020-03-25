# -*- coding: utf-8 -*-

from .context import mlspeclib
from mlspeclib.core import PopulateRegistry
from mlspeclib.schemavalidator import SchemaValidator
from pathlib import Path
from ruamel.yaml import YAML
from ruamel.yaml.compat import StringIO

import unittest


class BasicTestSuite(unittest.TestCase):
    """Basic test cases."""
    def test_instantiate_validator(self):
        s = SchemaValidator()
        self.assertIsInstance(s, SchemaValidator)

    def test_load_allowed_list_schema(self):
        yaml = YAML(typ='safe')
        s = SchemaValidator()

        schema_text = """
            storage_connection_type: 
                type: string
                allowed: [
                    'AWS_BLOB', # AWS Blob
                ]"""

        s.schema = yaml.load(schema_text)

        value_text = """
            storage_connection_type: AWS_BLOB
        """

        s.validate(yaml.load(value_text))
        assert len(s.errors) == 0

    def test_load_uuid_field(self):
        yaml = YAML(typ='safe')
        s = SchemaValidator()

        schema_text = """
            run_id: 
                type: uuid
                required: true
            """

        s.schema = yaml.load(schema_text)

        s.validate(yaml.load("run_id: f4bd7cee-42f9-4f29-a21e-3f78a9bad121"))
        assert len(s.errors) == 0

        # Below contains an 'x' in position 2
        s.validate(yaml.load("run_id: fxbd7cee-42f9-4f29-a21e-3f78a9bad121"))
        assert len(s.errors) == 1

    def test_load_semver_field(self):
        yaml = YAML(typ='safe')
        s = SchemaValidator()

        schema_text = """
            schema_version:
                type: semver
                required: true
            """
        s.schema = yaml.load(schema_text)

        s.validate(yaml.load("schema_version: 0.0.1"))
        assert len(s.errors) == 0

        # Below contains an 'x' in position 2
        s.validate(yaml.load("schema_version: x.x.x"))
        assert len(s.errors) == 1
        

if __name__ == '__main__':
    unittest.main()