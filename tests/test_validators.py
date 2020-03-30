# -*- coding: utf-8 -*-
from .context import mlspeclib

from mlspeclib.helpers import convert_to_yaml
from mlspeclib.schemavalidator import SchemaValidator

import unittest

class MockField():
    name = "MockField"

class ValidatorsTestSuite(unittest.TestCase):
    """Validators test cases."""

    def test_semver_found(self):
        v = SchemaValidator()
        assert v._validate_type_semver('0.0.1')

    def test_semver_not_found(self):
        v = SchemaValidator()
        assert not v._validate_type_semver('x.x.x')

    def test_uuid_found(self):
        v = SchemaValidator()
        self.assertTrue(v._validate_type_uuid('a04bf86c-90bc-4869-8851-b200c7ad3ccd'))

    def test_uuid_not_found(self):
        v = SchemaValidator()
        self.assertFalse(v._validate_type_uuid(''))

    def test_uri_valid(self):
        v = SchemaValidator()
        self.assertTrue(v._validate_type_URI('https://s3.us-west-2.amazonaws.com/mybucket/puppy.jpg'))
        self.assertTrue(v._validate_type_URI('S3://mybucket/puppy.jpg'))

    def test_uri_invalid(self):
        v = SchemaValidator()
        assert not v._validate_type_URI('xxx')
        assert not v._validate_type_URI('123')

    def test_regex_valid(self):
        v = SchemaValidator()

        regex_schema = """
all_letters:
    type: string
    regex: '[a-zA-Z]+'"""

        v.schema = convert_to_yaml(regex_schema)

        self.assertTrue(v.validate(convert_to_yaml("""all_letters: abcde""")))

        # Needs to be in quotes to be cast as string
        self.assertFalse(v.validate(convert_to_yaml("""all_letters: '129381'"""))) 

    @unittest.skip("Testing for invalid regex not yet implemented by cerberus")
    def test_regex_invalid(self):
        v = SchemaValidator()

        invalid_regex_schema = """
all_letters:
    type: string
    regex: '['"""

        v.schema = convert_to_yaml(invalid_regex_schema)
        
        self.assertTrue(v.validate(convert_to_yaml("""all_letters: abcde""")))
        self.assertFalse(v.validate(convert_to_yaml("""all_letters: '129381'"""))) # Needs to be in quotes to be cast as string


if __name__ == '__main__':
    unittest.main()