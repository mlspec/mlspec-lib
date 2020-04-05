# pylint: disable=protected-access,missing-function-docstring, missing-class-docstring, missing-module-docstring
# -*- coding: utf-8 -*-
import unittest

from mlspeclib.helpers import convert_yaml_to_dict, merge_two_dicts, \
                              check_and_return_schema_type_by_string, \
                              get_class_name
from mlspeclib.schemaenums import SchemaTypes

from tests.sample_schemas import SampleSchema

class HelpersTestSuite(unittest.TestCase):
    """Helpers test cases."""

    def test_check_and_return_schema_type_by_string_valid(self):
        self.assertIsInstance(check_and_return_schema_type_by_string('base'), SchemaTypes)

    def test_check_and_return_schema_type_by_string_invalid(self):
        with self.assertRaises(KeyError) as context:
            check_and_return_schema_type_by_string('xxxx')

        self.assertTrue("is not an enum from mlspeclib.schemacatalog.SchemaTypes"\
                                                            in str(context.exception))

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

    def test_get_class_name(self):
        self.assertIsNone(get_class_name(None, None))
        self.assertIsNone(get_class_name("0.0.1", None))
        self.assertIsNone(get_class_name(None, "base_name"))
        self.assertEqual(get_class_name("0.0.1", "base_name"), "0_0_1_base_name")
        self.assertEqual(get_class_name("xxxxx", "yyyyy"), "xxxxx_yyyyy")

if __name__ == '__main__':
    unittest.main()
