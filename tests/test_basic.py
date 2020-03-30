# -*- coding: utf-8 -*-

from .context import mlspeclib
from mlspeclib.helpers import convert_to_yaml

from mlspeclib.core import PopulateRegistry
from mlspeclib.schemavalidator import SchemaValidator
from tests.sample_schemas import SampleSchema
from pathlib import Path

import unittest


class BasicTestSuite(unittest.TestCase):
    """Basic test cases."""
    def test_instantiate_validator(self):
        s = SchemaValidator()
        self.assertIsInstance(s, SchemaValidator)

    def test_load_allowed_list_schema(self):
        s = SchemaValidator()

        schema_text = """
            storage_connection_type: 
                type: string
                allowed:
                    - 'AWS_BLOB' # AWS Blob"""

        # Ideally this would not be necessary - we'd be able to overload
        # the assignment to schema with a conversion.
        # TODO: Swap out the below with a conversion after assignment
        s.schema = convert_to_yaml(schema_text)

        value_text = """
            storage_connection_type: AWS_BLOB
        """

        s.validate(convert_to_yaml(value_text))
        assert len(s.errors) == 0

    def test_load_uuid_field(self):
        s = SchemaValidator()

        schema_text = """
            run_id: 
                type: uuid
                required: true
            """

        s.schema = convert_to_yaml(schema_text)

        s.validate(convert_to_yaml("run_id: f4bd7cee-42f9-4f29-a21e-3f78a9bad121"))
        assert len(s.errors) == 0

        # Below contains an 'x' in position 2
        s.validate(convert_to_yaml("run_id: fxbd7cee-42f9-4f29-a21e-3f78a9bad121"))
        assert len(s.errors) == 1

    def test_load_semver_field(self):
        s = SchemaValidator()

        schema_text = """
            schema_version:
                type: semver
                required: true
            """
        s.schema = convert_to_yaml(schema_text)

        s.validate(convert_to_yaml("schema_version: 0.0.1"))
        assert len(s.errors) == 0

        # Below contains an 'x' in position 2
        s.validate(convert_to_yaml("schema_version: x.x.x"))
        assert len(s.errors) == 1
        
    def test_load_datetime_field(self):
        s = SchemaValidator()

        schema_text = """
            run_date:
                type: datetime
                required: true
            """
        s.schema = convert_to_yaml(schema_text)


        s.validate(convert_to_yaml("run_date: 2020-03-25 14:17:38.977105"))
        assert len(s.errors) == 0

        s.validate(convert_to_yaml("run_date: 2020-03-25 14:17:38"))
        assert len(s.errors) == 0

        s.validate(convert_to_yaml("run_date: 1970-01-01 00:00:00.00000"))
        assert len(s.errors) == 0

        # Need to change normalizer (when I get feedback on this question: https://stackoverflow.com/questions/60857523/using-custom-validation-for-built-in-types)
        s.validate(convert_to_yaml("run_date: xxxxx"))
        assert len(s.errors) == 1    

    def test_load_full_base_schema(self):
        s = SchemaValidator()
        s.schema = convert_to_yaml(SampleSchema.SCHEMAS.BASE)
        s.validate(convert_to_yaml(SampleSchema.SUBMISSIONS.BASE))
        assert len(s.errors) == 0

    def test_load_full_datatype_schema(self):
        s = SchemaValidator()
        s.schema = convert_to_yaml(SampleSchema.SCHEMAS.DATATYPE)
        s.validate(convert_to_yaml(SampleSchema.SUBMISSIONS.DATATYPE))
        assert len(s.errors) == 0

if __name__ == '__main__':
    unittest.main()