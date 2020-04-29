# pylint: disable=protected-access,missing-function-docstring, missing-class-docstring, missing-module-docstring, no-self-use, line-too-long # noqa
# -*- coding: utf-8 -*-
import unittest

from marshmallow.validate import ValidationError
from marshmallow import fields

from mlspeclib.helpers import convert_yaml_to_dict, merge_two_dicts
from mlspeclib.mlobject import MLObject
from mlspeclib.mlschema import MLSchema
from mlspeclib.mlschemavalidators import MLSchemaValidators
from tests.sample_schemas import SampleSchema
from tests.sample_submissions import SampleSubmissions


class ValidatorsTestSuite(unittest.TestCase):
    """Validators test cases."""

    schema_schema_info = convert_yaml_to_dict(
        """
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
"""
    )
    submission_schema_info = {"schema_version": "0.0.1", "schema_type": "base"}

    def test_semver_found(self):
        assert MLSchemaValidators.validate_type_semver("0.0.1")

    def test_semver_not_found(self):
        assert not MLSchemaValidators.validate_type_semver("x.x.x")

    def test_uuid_found(self):
        instantiated_object = self.generic_schema_validator(
            SampleSchema.TEST.UUID, SampleSubmissions.UNIT_TESTS.UUID_VALID
        )
        self.assertTrue(instantiated_object["run_id"])

    def test_uuid_not_found(self):
        self.generic_schema_validator(
            SampleSchema.TEST.UUID,
            SampleSubmissions.UNIT_TESTS.UUID_INVALID,
            ValidationError,
        )

    def test_uri_valid(self):
        instantiated_object = self.generic_schema_validator(
            SampleSchema.TEST.URI, SampleSubmissions.UNIT_TESTS.URI_VALID_1
        )
        self.assertTrue(instantiated_object["endpoint"])

        instantiated_object = self.generic_schema_validator(
            SampleSchema.TEST.URI, SampleSubmissions.UNIT_TESTS.URI_VALID_2
        )
        self.assertTrue(instantiated_object["endpoint"])

    def test_uri_invalid(self):
        self.generic_schema_validator(
            SampleSchema.TEST.URI,
            SampleSubmissions.UNIT_TESTS.URI_INVALID_1,
            ValidationError,
        )
        self.generic_schema_validator(
            SampleSchema.TEST.URI,
            SampleSubmissions.UNIT_TESTS.URI_INVALID_2,
            ValidationError,
        )

    def test_regex_valid(self):
        instantiated_object = self.generic_schema_validator(
            SampleSchema.TEST.REGEX, SampleSubmissions.UNIT_TESTS.REGEX_ALL_LETTERS
        )
        self.assertTrue(instantiated_object["all_letters"])

        self.generic_schema_validator(
            SampleSchema.TEST.REGEX,
            SampleSubmissions.UNIT_TESTS.REGEX_ALL_NUMBERS,
            ValidationError,
        )

    def test_regex_invalid(self):
        self.generic_schema_validator(
            SampleSchema.TEST.INVALID_REGEX,
            None,
            AssertionError,
        )

    @unittest.skip("NYI")
    def test_path(self):
        self.assertTrue(False)

    @unittest.skip("NYI")
    def test_bucket(self):
        self.assertTrue(False)

    def test_interfaces_valid(self):
        instantiated_object = self.generic_schema_validator(
            SampleSchema.TEST.INTERFACE,
            SampleSubmissions.UNIT_TESTS.INTERFACE_VALID_UNNAMED,
        )
        self.assertTrue(len(instantiated_object["inputs"]) == 2)

        instantiated_object = self.generic_schema_validator(
            SampleSchema.TEST.INTERFACE,
            SampleSubmissions.UNIT_TESTS.INTERFACE_VALID_NAMED,
        )
        self.assertTrue(len(instantiated_object["inputs"]) == 2)

    @unittest.skip("Type is not required in KFP (but it should be)")
    def test_interfaces_missing_type(self):
        self.generic_schema_validator(
            SampleSchema.TEST.INTERFACE,
            SampleSubmissions.UNIT_TESTS.INTERFACE_INVALID_MISSING_TYPE,
            ValidationError,
            "No type",
        )

    def test_interfaces_mismatch_type(self):
        self.generic_schema_validator(
            SampleSchema.TEST.INTERFACE,
            SampleSubmissions.UNIT_TESTS.INTERFACE_INVALID_MISMATCH_TYPE,
            ValidationError,
            "valid default",
        )

    def test_interfaces_type_unknown(self):
        self.generic_schema_validator(
            SampleSchema.TEST.INTERFACE,
            SampleSubmissions.UNIT_TESTS.INTERFACE_INVALID_TYPE_UNKNOWN_1,
            ValidationError,
            "string or a dict",
        )

    def test_validate_constraints_constraint_valid_greater_equal(self):
        this_schema = MLSchema.create_schema(
            self.wrap_schema_with_mlschema_info(SampleSchema.TEST.OPERATOR_VALID)
        )

        self.assertTrue(isinstance(this_schema.declared_fields["num"], fields.Integer))

    def test_validate_constraints_constraint_valid_modulo(self):
        this_schema = MLSchema.create_schema(
            self.wrap_schema_with_mlschema_info(SampleSchema.TEST.OPERATOR_VALID_MODULO)
        )

        self.assertTrue(isinstance(this_schema.declared_fields["num"], fields.Integer))

    def test_validate_constraints_true_value(self):
        instantiated_object = self.generic_schema_validator(
            SampleSchema.TEST.OPERATOR_VALID,
            SampleSubmissions.UNIT_TESTS.CONSTRAINT_VALID_MORE_THAN_1000,
            None,
        )
        self.assertTrue(isinstance(instantiated_object["num"], int))

    def test_validate_constraints_false_value(self):
        self.generic_schema_validator(
            SampleSchema.TEST.OPERATOR_VALID,
            SampleSubmissions.UNIT_TESTS.CONSTRAINT_VALID_LESS_THAN_1000,
            ValidationError,
        )

    def test_validate_constraints_modulo_true(self):
        instantiated_object = self.generic_schema_validator(
            SampleSchema.TEST.OPERATOR_VALID_MODULO_2,
            SampleSubmissions.UNIT_TESTS.CONSTRAINT_VALID_MODULO_2_TRUE,
            ValidationError,
        )
        self.assertTrue(isinstance(instantiated_object["num"], int))

    def test_validate_constraints_modulo_false(self):
        self.generic_schema_validator(
            SampleSchema.TEST.OPERATOR_VALID_MODULO_2,
            SampleSubmissions.UNIT_TESTS.CONSTRAINT_VALID_MODULO_2_FALSE,
            ValidationError,
        )

    def test_validate_constraints_constraint_invalid_type(self):
        self.generic_schema_validator(
            SampleSchema.TEST.OPERATOR_INVALID_TYPE,
            None,
            ValueError,
            "Attempting to add",
        )

    def test_validate_constraints_constraint_no_valid_operator(self):
        self.generic_schema_validator(
            SampleSchema.TEST.OPERATOR_INVALID_NO_OPERATOR,
            None,
            ValueError,
            "a valid constraint",
        )

    def test_validate_constraints_constraint_invalid_operator(self):
        self.generic_schema_validator(
            SampleSchema.TEST.OPERATOR_INVALID_BAD_OPERATOR,
            None,
            ValueError,
            "a valid operator",
        )

    def test_validate_constraints_constraint_invalid_number(self):
        self.generic_schema_validator(
            SampleSchema.TEST.OPERATOR_INVALID_STRING,
            None,
            ValueError,
            "a valid number",
        )

    def test_validate_constraints_constraint_extra_characters(self):
        self.generic_schema_validator(
            SampleSchema.TEST.OPERATOR_INVALID_BAD_EQUATION,
            None,
            ValueError,
            "extra characters",
        )

    def generic_schema_validator(
        self, test_schema, test_submission, exception_type=None, exception_string=None
    ) -> MLObject:
        error_string = None
        try:
            instantiated_schema = MLSchema.create_schema(
                self.wrap_schema_with_mlschema_info(test_schema)
            )  # noqa
        except Exception as e:
            self.assertTrue(isinstance(e, exception_type))
            error_string = str(e)

        if test_submission is not None:
            yaml_submission = convert_yaml_to_dict(
                self.wrap_submission_with_mlschema_info(test_submission)
            )  # noqa

            if exception_type is not None:
                with self.assertRaises(exception_type) as context:
                    instantiated_schema.load(yaml_submission)

                if context is not None:
                    error_string = str(context.exception)

        # if error string is not none, we threw an error, return
        if error_string is not None:
            if exception_string is not None:
                self.assertTrue(exception_string in error_string)
            return  # Raised an exception during loading dict, return

        return instantiated_schema.load(yaml_submission)

    def wrap_schema_with_mlschema_info(self, this_dict):
        return merge_two_dicts(self.schema_schema_info, convert_yaml_to_dict(this_dict))

    def wrap_submission_with_mlschema_info(self, this_dict):
        return merge_two_dicts(
            self.submission_schema_info, convert_yaml_to_dict(this_dict)
        )


if __name__ == "__main__":
    unittest.main()
