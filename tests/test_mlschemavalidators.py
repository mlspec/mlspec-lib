# pylint: disable=protected-access,missing-function-docstring, missing-class-docstring, missing-module-docstring, no-self-use
# -*- coding: utf-8 -*-
import unittest

from marshmallow.validate import ValidationError

from mlspeclib.helpers import convert_yaml_to_dict
from mlspeclib.mlschema import MLSchema
from mlspeclib.mlschemavalidators import MLSchemaValidators
from tests.sample_schemas import SampleSchema
from tests.sample_submissions import SampleSubmissions

class ValidatorsTestSuite(unittest.TestCase):
    """Validators test cases."""

    def test_semver_found(self):
        assert MLSchemaValidators.validate_type_semver('0.0.1')

    def test_semver_not_found(self):
        assert not MLSchemaValidators.validate_type_semver('x.x.x')

    def test_uuid_found(self):
        instantiated_schema = MLSchema.create(SampleSchema.TEST.UUID)
        yaml_submission = convert_yaml_to_dict(SampleSubmissions.UNIT_TESTS.UUID_VALID)
        instantiated_object = instantiated_schema.load(yaml_submission)

        self.assertTrue(instantiated_object['run_id'])

    def test_uuid_not_found(self):
        instantiated_schema = MLSchema.create(SampleSchema.TEST.UUID)
        yaml_submission = convert_yaml_to_dict(SampleSubmissions.UNIT_TESTS.UUID_INVALID)
        with self.assertRaises(ValidationError):
            instantiated_schema.load(yaml_submission)

    def test_uri_valid(self):
        instantiated_schema = MLSchema.create(SampleSchema.TEST.URI)
        yaml_submission = convert_yaml_to_dict(SampleSubmissions.UNIT_TESTS.URI_VALID_1)
        instantiated_object = instantiated_schema.load(yaml_submission)

        self.assertTrue(instantiated_object['endpoint'])

        yaml_submission = convert_yaml_to_dict(SampleSubmissions.UNIT_TESTS.URI_VALID_2)
        instantiated_object = instantiated_schema.load(yaml_submission)

        self.assertTrue(instantiated_object['endpoint'])

    def test_uri_invalid(self):
        instantiated_schema = MLSchema.create(SampleSchema.TEST.URI)
        yaml_submission = convert_yaml_to_dict(SampleSubmissions.UNIT_TESTS.URI_INVALID_1)
        with self.assertRaises(ValidationError):
            instantiated_schema.load(yaml_submission)

        yaml_submission = convert_yaml_to_dict(SampleSubmissions.UNIT_TESTS.URI_INVALID_2)
        with self.assertRaises(ValidationError):
            instantiated_schema.load(yaml_submission)

    def test_regex_valid(self):
        instantiated_schema = MLSchema.create(SampleSchema.TEST.REGEX)
        yaml_submission = convert_yaml_to_dict(SampleSubmissions.UNIT_TESTS.REGEX_ALL_LETTERS)
        instantiated_object = instantiated_schema.load(yaml_submission)

        self.assertTrue(instantiated_object['all_letters'])

        yaml_submission = convert_yaml_to_dict(SampleSubmissions.UNIT_TESTS.REGEX_ALL_NUMBERS)
        with self.assertRaises(ValidationError):
            instantiated_schema.load(yaml_submission)

    def test_regex_invalid(self):
        with self.assertRaises(AssertionError):
            MLSchema.create(SampleSchema.TEST.INVALID_REGEX)

if __name__ == '__main__':
    unittest.main()
