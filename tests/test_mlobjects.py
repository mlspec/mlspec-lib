# pylint: disable=protected-access,missing-function-docstring, missing-class-docstring, missing-module-docstring
# -*- coding: utf-8 -*-
""" Test cases for MLObjects """

import unittest

import mlspeclib
from typing import types
from dataclasses import is_dataclass

from mlspeclib.schemaenums import SchemaTypes
from mlspeclib.mlobjects import GenericMLObject, MLObjectsDict, MLObject

from tests.sample_submissions import SampleSubmissions

@unittest.skip("NYI")
class MLObjectsTestSuite(unittest.TestCase):
    """MLObjects test cases."""

    def test_instantiate_inherited_mlobject(self):
        """Inherit from generic ml object and instantiate a base object"""

        base_class_object = type('Base', (GenericMLObject,), { \
                                 'schema_enum': SchemaTypes.BASE})
        instanted_object = base_class_object()

        self.assertIsInstance(instanted_object, base_class_object)

    def test_create_base_object_from_yaml(self):
        """Inherit from generic ml object and instantiate a base object"""

        ml_object_dict = MLObjectsDict()
        submission_yaml = mlspeclib.helpers.convert_yaml_to_dict(SampleSubmissions.FULL_SUBMISSIONS.BASE)
        # base_object = ml_object_dict.create_object(submission_yaml['schema_type'])

        # self.assertTrue(base_object['schema_type'], SchemaTypes.BASE)

    @unittest.skip("NYI")
    def test_create_empty_ml_object(self):
        """ Create empty MLObject """
        ml_object = MLObject.create_object_type({})

        self.assertTrue(is_dataclass(ml_object) and not isinstance(ml_object, MLObject))

    @unittest.skip("NYI")
    def test_create_a_single_ml_object(self):
        """ Create with a single field """
        ml_object = MLObject.create_object_type({'schema_enum': '0.0.1'})

        self.assertTrue(is_dataclass(ml_object) and not isinstance(ml_object, MLObject))
        self.assertTrue(ml_object.schema_enum == '0.0.1')

    @unittest.skip("NYI")
    def test_create_flat_ml_object(self):
        """ Just testing create with flat fields as dict"""

        two_fields = {'one': 1, 'two': 'second'}

        ml_object = MLObject.create_object_type(two_fields)

        self.assertTrue(ml_object.one == 1)
