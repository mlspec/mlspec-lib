# pylint: disable=protected-access,missing-function-docstring, missing-class-docstring, missing-module-docstring
# -*- coding: utf-8 -*-
import unittest

from mlspeclib.helpers import convert_to_yaml
from mlspeclib.metadatavalidator import MetadataValidator

class MockField():
    name = "MockField"

class ValidatorsTestSuite(unittest.TestCase):
    """Validators test cases."""

    def test_semver_found(self):
        metadata_validator = MetadataValidator()
        assert metadata_validator._validate_type_semver('0.0.1')

    def test_semver_not_found(self):
        metadata_validator = MetadataValidator()
        assert not metadata_validator._validate_type_semver('x.x.x')

    def test_uuid_found(self):
        metadata_validator = MetadataValidator()
        self.assertTrue(metadata_validator._validate_type_uuid(\
                                'a04bf86c-90bc-4869-8851-b200c7ad3ccd'))

    def test_uuid_not_found(self):
        metadata_validator = MetadataValidator()
        self.assertFalse(metadata_validator._validate_type_uuid(''))

    def test_uri_valid(self):
        metadata_validator = MetadataValidator()
        self.assertTrue(metadata_validator._validate_type_URI(\
                            'https://s3.us-west-2.amazonaws.com/mybucket/puppy.jpg'))
        self.assertTrue(metadata_validator._validate_type_URI(\
                            'S3://mybucket/puppy.jpg'))

    def test_uri_invalid(self):
        metadata_validator = MetadataValidator()
        assert not metadata_validator._validate_type_URI('xxx')
        assert not metadata_validator._validate_type_URI('123')

    def test_regex_valid(self):
        metadata_validator = MetadataValidator()

        regex_schema = """
all_letters:
    type: string
    regex: '[a-zA-Z]+'"""

        metadata_validator.schema = convert_to_yaml(regex_schema)

        self.assertTrue(metadata_validator.validate(convert_to_yaml("""all_letters: abcde""")))

        # Needs to be in quotes to be cast as string
        self.assertFalse(metadata_validator.validate(convert_to_yaml("""all_letters: '129381'""")))

    @unittest.skip("Testing for invalid regex not yet implemented by cerberus")
    def test_regex_invalid(self):
        metadata_validator = MetadataValidator()

        invalid_regex_schema = """
all_letters:
    type: string
    regex: '['"""

        metadata_validator.schema = convert_to_yaml(invalid_regex_schema)

        self.assertTrue(metadata_validator.validate(convert_to_yaml("""all_letters: abcde""")))

        # Needs to be in quotes to be cast as string
        self.assertFalse(metadata_validator.validate(convert_to_yaml("""all_letters: '129381'""")))

if __name__ == '__main__':
    unittest.main()
