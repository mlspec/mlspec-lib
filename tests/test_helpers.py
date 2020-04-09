# pylint: disable=protected-access,missing-function-docstring, missing-class-docstring, missing-module-docstring
# -*- coding: utf-8 -*-
import unittest

from mlspeclib.helpers import convert_yaml_to_dict, merge_two_dicts, \
                              check_and_return_schema_type_by_string, \
                              recursive_fromkeys
from mlspeclib.mlschemaenums import MLSchemaTypes

from tests.sample_schemas import SampleSchema

class HelpersTestSuite(unittest.TestCase):
    """Helpers test cases."""

    def test_check_and_return_schema_type_by_string_valid(self):
        self.assertIsInstance(check_and_return_schema_type_by_string('base'), MLSchemaTypes)

    def test_check_and_return_schema_type_by_string_invalid(self):
        with self.assertRaises(KeyError) as context:
            check_and_return_schema_type_by_string('xxxx')

        self.assertTrue("MLSchemaTypes" in str(context.exception))

    def test_merge_two_dicts(self):
        dict1 = convert_yaml_to_dict(SampleSchema.TEST.ONE)
        dict2 = convert_yaml_to_dict(SampleSchema.TEST.TWO_THAT_REFERENCES_ONE)

        dict2 = merge_two_dicts(dict1, dict2)

        # Should not work, dict1 should be unchanged
        with self.assertRaises(KeyError):
            dict1['foo'] == 1 # pylint: disable=pointless-statement

        self.assertTrue(dict1['qaz'] == 'a')

        # Should work - dict2 is the merge target
        self.assertTrue(dict2['qaz'] == 'a')
        self.assertTrue(dict2['foo'] == 1)

    def test_recursive_fromkeys(self):
        this_dict = {'a': 1, 'b': 'a', 'c':{'d': ('x','z'), 'e': 7, 'f': {'g': None}, 'h': {}}, 'i': print}
        return_dict = recursive_fromkeys(this_dict)

        self.assertTrue(return_dict['a'] is None)
        self.assertTrue(return_dict['b'] is None)
        self.assertIsInstance(return_dict['c'], dict)
        self.assertTrue(len(return_dict['c']) == 4)
        self.assertTrue(return_dict['c']['d'] is None)
        self.assertTrue(return_dict['c']['e'] is None)
        self.assertIsInstance(return_dict['c']['f'], dict)
        self.assertTrue(return_dict['c']['f']['g'] is None)
        self.assertIsInstance(return_dict['c']['h'], dict)
        self.assertTrue(len(return_dict['c']['h']) == 0)
        self.assertTrue(return_dict['i'] is None)

if __name__ == '__main__':
    unittest.main()
