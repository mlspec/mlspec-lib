# pylint: disable=protected-access,missing-function-docstring, missing-class-docstring, missing-module-docstring, no-self-use, line-too-long # noqa
# -*- coding: utf-8 -*-
import unittest

from marshmallow.validate import ValidationError

from mlspeclib.helpers import convert_yaml_to_dict, merge_two_dicts
from mlspeclib.mlschema import MLSchema
from mlspeclib.mlschemavalidators import MLSchemaValidators
from tests.sample_schemas import SampleSchema
from tests.sample_submissions import SampleSubmissions


class ValidatorsTestSuite(unittest.TestCase):
    """Validators test cases."""

    schema_schema_info = convert_yaml_to_dict("""
mlspec_schema_version:
    # Identifies the version of this schema
    meta: 0.0.1

mlspec_schema_type:
    # Base schema type that this extends
    meta: base

schema_version:
  # Identifies version of MLSpec to use
  type: semver
  required: True
schema_type:
  # Identifies version of MLSpec to use
  type: allowed_schema_types
  required: True
""")
    submission_schema_info = {'schema_version': '0.0.1', 'schema_type': 'base'}

    def test_semver_found(self):
        assert MLSchemaValidators.validate_type_semver('0.0.1')

    def test_semver_not_found(self):
        assert not MLSchemaValidators.validate_type_semver('x.x.x')

    def test_uuid_found(self):
        instantiated_schema = MLSchema.create_schema(self.wrap_schema_with_mlschema_info(SampleSchema.TEST.UUID))  # noqa
        yaml_submission = convert_yaml_to_dict(self.wrap_submission_with_mlschema_info(SampleSubmissions.UNIT_TESTS.UUID_VALID)) # noqa
        instantiated_object = instantiated_schema.load(yaml_submission)

        self.assertTrue(instantiated_object['run_id'])

    def test_uuid_not_found(self):
        instantiated_schema = MLSchema.create_schema(self.wrap_schema_with_mlschema_info(SampleSchema.TEST.UUID))  # noqa
        yaml_submission = convert_yaml_to_dict(self.wrap_submission_with_mlschema_info(SampleSubmissions.UNIT_TESTS.UUID_INVALID)) # noqa
        with self.assertRaises(ValidationError):
            instantiated_schema.load(yaml_submission)

    def test_uri_valid(self):
        instantiated_schema = MLSchema.create_schema(self.wrap_schema_with_mlschema_info(SampleSchema.TEST.URI)) # noqa
        yaml_submission = convert_yaml_to_dict(self.wrap_submission_with_mlschema_info(SampleSubmissions.UNIT_TESTS.URI_VALID_1))  # noqa
        instantiated_object = instantiated_schema.load(yaml_submission)

        self.assertTrue(instantiated_object['endpoint'])

        yaml_submission = convert_yaml_to_dict(self.wrap_submission_with_mlschema_info(SampleSubmissions.UNIT_TESTS.URI_VALID_2)) # noqa
        instantiated_object = instantiated_schema.load(yaml_submission)

        self.assertTrue(instantiated_object['endpoint'])

    def test_uri_invalid(self):
        instantiated_schema = MLSchema.create_schema(self.wrap_schema_with_mlschema_info(SampleSchema.TEST.URI))  # noqa
        yaml_submission = convert_yaml_to_dict(self.wrap_submission_with_mlschema_info(SampleSubmissions.UNIT_TESTS.URI_INVALID_1))  # noqa
        with self.assertRaises(ValidationError):
            instantiated_schema.load(yaml_submission)

        yaml_submission = convert_yaml_to_dict(self.wrap_submission_with_mlschema_info(SampleSubmissions.UNIT_TESTS.URI_INVALID_2))  # noqa
        with self.assertRaises(ValidationError):
            instantiated_schema.load(yaml_submission)

    def test_regex_valid(self):
        instantiated_schema = MLSchema.create_schema(self.wrap_schema_with_mlschema_info(SampleSchema.TEST.REGEX))  # noqa
        yaml_submission = convert_yaml_to_dict(self.wrap_submission_with_mlschema_info(SampleSubmissions.UNIT_TESTS.REGEX_ALL_LETTERS))  # noqa
        instantiated_object = instantiated_schema.load(yaml_submission)

        self.assertTrue(instantiated_object['all_letters'])

        yaml_submission = convert_yaml_to_dict(self.wrap_submission_with_mlschema_info(SampleSubmissions.UNIT_TESTS.REGEX_ALL_NUMBERS))  # noqa
        with self.assertRaises(ValidationError):
            instantiated_schema.load(yaml_submission)

    def test_regex_invalid(self):
        with self.assertRaises(AssertionError):
            MLSchema.create_schema(self.wrap_schema_with_mlschema_info(SampleSchema.TEST.INVALID_REGEX))  # noqa

    @unittest.skip("NYI")
    def test_path(self):
        self.assertTrue(False)

    @unittest.skip("NYI")
    def test_bucket(self):
        self.assertTrue(False)

    def test_interfaces_valid(self):
        instantiated_schema = MLSchema.create_schema(self.wrap_schema_with_mlschema_info(SampleSchema.TEST.INTERFACE)) # noqa
        yaml_submission = convert_yaml_to_dict(self.wrap_submission_with_mlschema_info(SampleSubmissions.UNIT_TESTS.INTERFACE_VALID_UNNAMED))  # noqa
        instantiated_object = instantiated_schema.load(yaml_submission)

        self.assertTrue(len(instantiated_object['inputs']) == 2)

        yaml_submission = convert_yaml_to_dict(self.wrap_submission_with_mlschema_info(SampleSubmissions.UNIT_TESTS.INTERFACE_VALID_NAMED))  # noqa
        instantiated_object = instantiated_schema.load(yaml_submission)

        self.assertTrue(len(instantiated_object['inputs']) == 2)

    @unittest.skip("Type is not required in KFP (but it should be)")
    def test_interfaces_missing_type(self):
        instantiated_schema = MLSchema.create_schema(self.wrap_schema_with_mlschema_info(SampleSchema.TEST.INTERFACE)) # noqa
        yaml_submission = convert_yaml_to_dict(self.wrap_submission_with_mlschema_info(SampleSubmissions.UNIT_TESTS.INTERFACE_INVALID_MISSING_TYPE))  # noqa

        with self.assertRaises(ValidationError) as context:
            instantiated_schema.load(yaml_submission)

        self.assertTrue('No type' in context.exception.messages['inputs'][0][0])

    def test_interfaces_mismatch_type(self):
        instantiated_schema = MLSchema.create_schema(self.wrap_schema_with_mlschema_info(SampleSchema.TEST.INTERFACE)) # noqa
        yaml_submission = convert_yaml_to_dict(self.wrap_submission_with_mlschema_info(SampleSubmissions.UNIT_TESTS.INTERFACE_INVALID_MISMATCH_TYPE))  # noqa

        with self.assertRaises(ValidationError) as context:
            instantiated_schema.load(yaml_submission)

        self.assertTrue('valid default' in context.exception.messages['inputs'][0][0])

    def test_interfaces_type_unknown(self):
        instantiated_schema = MLSchema.create_schema(self.wrap_schema_with_mlschema_info(SampleSchema.TEST.INTERFACE)) # noqa
        yaml_submission = convert_yaml_to_dict(self.wrap_submission_with_mlschema_info(SampleSubmissions.UNIT_TESTS.INTERFACE_INVALID_TYPE_UNKNOWN_1))  # noqa

        with self.assertRaises(ValidationError) as context:
            instantiated_schema.load(yaml_submission)

        self.assertTrue('string or a dict' in context.exception.messages['inputs'][0][0])

    def wrap_schema_with_mlschema_info(self, this_dict):
        return merge_two_dicts(self.schema_schema_info, convert_yaml_to_dict(this_dict))

    def wrap_submission_with_mlschema_info(self, this_dict):
        return merge_two_dicts(self.submission_schema_info, convert_yaml_to_dict(this_dict))


if __name__ == '__main__':
    unittest.main()
