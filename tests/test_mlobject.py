# pylint: disable=protected-access,missing-function-docstring, missing-class-docstring, missing-module-docstring, missing-class-docstring
# -*- coding: utf-8 -*-
import unittest

import semver as SemVer

from marshmallow import pprint

from mlspeclib.mlschemaenums import MLSchemaTypes

from mlspeclib.mlobject import MLObject
from mlspeclib.mlschema import MLSchema

class test_mlobject(unittest.TestCase): #pylint: disable=invalid-name
    """MLobject test cases."""
    def test_create_ml_object(self):
        ml_object = MLObject()
        ml_object.set_semver_and_type('0.0.1', MLSchemaTypes.DATAPATH)

        self.assertIsNotNone(ml_object)
        self.assertTrue(ml_object.version() == '0.0.1')
        self.assertTrue(ml_object.schema_type() == MLSchemaTypes.DATAPATH)

    def test_create_bad_semver(self):
        ml_object = MLObject()
        with self.assertRaises(ValueError):
            ml_object.set_semver_and_type('0.0.x', MLSchemaTypes.DATAPATH)

        with self.assertRaises(ValueError):
            ml_object.set_semver_and_type(None, MLSchemaTypes.DATAPATH)

    def test_create_bad_schema_type(self):
        ml_object = MLObject()
        with self.assertRaises(KeyError):
            ml_object.set_semver_and_type('0.0.1', 'foo')

    def test_create_stub_base_object(self):
        ml_object = MLObject()
        ml_object.set_semver_and_type('0.0.1', MLSchemaTypes.BASE)
        self.assertIsNone(ml_object['run_date'])
        self.assertTrue(len(ml_object) == 7)

    def test_create_stub_nested_object(self):
        ml_object = MLObject()
        ml_object.set_semver_and_type('0.0.1', MLSchemaTypes.DATAPATH)
        self.assertTrue(len(ml_object) == 10)
        self.assertIsNone(ml_object.run_date)
        self.assertTrue(len(ml_object.connection) == 3)
        self.assertIsNone(ml_object.connection.endpoint)

if __name__ == '__main__':
    unittest.main()
