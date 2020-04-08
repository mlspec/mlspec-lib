# pylint: disable=protected-access,missing-function-docstring, missing-class-docstring, missing-module-docstring, missing-class-docstring
# -*- coding: utf-8 -*-
import unittest

from pathlib import Path

from mlspeclib.mlschema import MLSchema
from mlspeclib.io import IO

class test_io(unittest.TestCase): #pylint: disable=invalid-name
    """io test cases."""
    def test_load_file_from_disk(self):
        all_objects = []

        MLSchema.populate_registry()

        for submission_file in list(Path('.').glob('tests/data/*.yaml')):
            all_objects.append(IO.get_object_from_path(submission_file))

        self.assertTrue(len(all_objects) > 1)

if __name__ == '__main__':
    unittest.main()
