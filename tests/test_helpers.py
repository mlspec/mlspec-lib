# pylint: disable=protected-access,missing-function-docstring, missing-class-docstring, missing-module-docstring
# -*- coding: utf-8 -*-
import unittest

from mlspeclib.helpers import (
    convert_yaml_to_dict,
    merge_two_dicts,
    check_and_return_schema_type_by_string,
    recursive_fromkeys,
    generate_lambda,
    get_schema_from_registry,
    schema_in_registry
)
from mlspeclib.mlschemaenums import MLSchemaTypes

from tests.sample_schemas import SampleSchema

from marshmallow import ValidationError

from io import StringIO
import logging
from unittest.mock import patch


class HelpersTestSuite(unittest.TestCase):
    """Helpers test cases."""

    # def test_check_and_return_schema_type_by_string_valid(self):
    #     self.assertIsInstance(
    #         check_and_return_schema_type_by_string("base"), MLSchemaTypes
    #     )

    # def test_check_and_return_schema_type_by_string_invalid(self):
    #     with self.assertRaises(KeyError) as context:
    #         check_and_return_schema_type_by_string("xxxx")

    #     self.assertTrue("MLSchemaTypes" in str(context.exception))

    def test_merge_two_dicts(self):
        dict1 = convert_yaml_to_dict(SampleSchema.TEST.ONE)
        dict2 = convert_yaml_to_dict(SampleSchema.TEST.TWO_THAT_REFERENCES_ONE)

        dict2 = merge_two_dicts(dict1, dict2)

        # Should not work, dict1 should be unchanged
        with self.assertRaises(KeyError):
            dict1["foo"] == 1  # pylint: disable=pointless-statement

        self.assertTrue(dict1["qaz"] == "a")

        # Should work - dict2 is the merge target
        self.assertTrue(dict2["qaz"] == "a")
        self.assertTrue(dict2["foo"] == 1)

    def test_recursive_fromkeys(self):
        class declared_fields_class(object):
            def __init__(self, this_dict):
                self._declared_fields = this_dict

        class dict_assigned_to_nested(object):
            def __init__(self, this_dict):
                self.nested = declared_fields_class(this_dict)

        f = dict_assigned_to_nested({"g": None})
        c = dict_assigned_to_nested({"d": ("x", "z"), "e": 7, "f": f, "h": {}})
        this_dict = {"a": 1, "b": "a", "c": c, "i": print}
        return_dict = recursive_fromkeys(this_dict)

        self.assertTrue(return_dict["a"] is None)
        self.assertTrue(return_dict["b"] is None)
        self.assertIsInstance(return_dict["c"], dict)
        self.assertTrue(len(return_dict["c"]) == 4)
        self.assertTrue(return_dict["c"]["d"] is None)
        self.assertTrue(return_dict["c"]["e"] is None)
        self.assertIsInstance(return_dict["c"]["f"], dict)
        self.assertTrue(return_dict["c"]["f"]["g"] is None)
        self.assertIsInstance(return_dict["c"]["h"], dict)
        self.assertTrue(len(return_dict["c"]["h"]) == 0)
        self.assertTrue(return_dict["i"] is None)

    def test_generate_lambda_none(self):
        with self.assertRaises(ValidationError) as context:
            generate_lambda(None)

        self.assertTrue("No value was " in str(context.exception))

    def test_generate_lambda_invalid(self):
        with self.assertRaises(ValidationError) as context:
            generate_lambda("xxx.xxx.000")

        self.assertTrue("No parsable lambda" in str(context.exception))

    def test_generate_lambda_more_than_one(self):
        with self.assertRaises(ValidationError) as context:
            generate_lambda("x > y > 10")

        self.assertTrue("Only one variable" in str(context.exception))

    def test_generate_lambda_no_variables(self):
        with self.assertRaises(ValidationError) as context:
            generate_lambda("11 > 10")

        self.assertTrue("No variables were" in str(context.exception))

    def test_generate_lambda_not_x(self):
        with self.assertRaises(ValidationError) as context:
            generate_lambda("y > 10")

        self.assertTrue("Only the variable" in str(context.exception))

    def test_generate_lambda_valid(self):
        fxn = generate_lambda("x % 8192 == 0")

        self.assertTrue(fxn(8192))

        self.assertFalse(fxn(8193))

    def test_get_invalid_schema_from_registry(self):
        mock_stdout = StringIO()
        rootLogger = logging.getLogger()
        rootLogger.addHandler(logging.StreamHandler(mock_stdout))

        schema_name = "bad_schema_name"

        with self.assertRaises(SystemExit) as cm:
            get_schema_from_registry(schema_name)
        
        return_string = mock_stdout.getvalue()
        assert schema_name in return_string
        self.assertEqual(cm.exception.code, 1)
        


if __name__ == "__main__":
    unittest.main()
