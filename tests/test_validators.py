# -*- coding: utf-8 -*-
from .context import mlspeclib
from mlspeclib import enums, validators
import unittest

class MockField():
    name = "MockField"

class ValidatorsTestSuite(unittest.TestCase):
    """Validators test cases."""

    def test_enum_found(self):
        validator = validators.Validators()
        assert validator.enum(enums.ConnectionTypes, "AWS_BLOB")

    def test_enum_not_found(self):
        validator = validators.Validators()
        assert not validator.enum(enums.ConnectionTypes, "INVALID_ENUM")

    def test_semver_found(self):
        validator = validators.Validators()
        assert validator.semver('0.0.1')

    def test_semver_not_found(self):
        validator = validators.Validators()
        assert not validator.semver('x.x.x')

if __name__ == '__main__':
    unittest.main()