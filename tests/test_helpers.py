# -*- coding: utf-8 -*-
from .context import mlspeclib
from mlspeclib.helpers import convert_to_yaml, merge_two_dicts
from tests.sample_schemas import SampleSchema

from ruamel.yaml.scanner import ScannerError

import unittest

class HelpersTestSuite(unittest.TestCase):
    """Helpers test cases."""
    def test_merge_two_dicts(self):
        dict1 = convert_to_yaml(SampleSchema.TEST.ONE)
        dict2 = convert_to_yaml(SampleSchema.TEST.TWO_THAT_REFERENCES_ONE)

        dict2 = merge_two_dicts(dict1, dict2)

        # Should not work, dict1 should be unchanged
        with self.assertRaises(KeyError):
            dict1['foo'] == 1

        self.assertTrue(dict1['qaz'] == 'a')

        # Should work - dict2 is the merge target
        self.assertTrue(dict2['qaz'] == 'a')
        self.assertTrue(dict2['foo'] == 1)

if __name__ == '__main__':
    unittest.main()