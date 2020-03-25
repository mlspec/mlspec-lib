# -*- coding: utf-8 -*-
from .context import mlspeclib
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
        assert v._validate_type_uuid('a04bf86c-90bc-4869-8851-b200c7ad3ccd')

    def test_uuid_not_found(self):
        v = SchemaValidator()
        assert not v._validate_type_uuid('')

if __name__ == '__main__':
    unittest.main()