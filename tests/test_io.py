# pylint: disable=protected-access,missing-function-docstring, missing-class-docstring, missing-module-docstring, missing-class-docstring
# -*- coding: utf-8 -*-
import unittest

from pathlib import Path

from marshmallow import pprint

from mlspeclib.mlschema import MLSchema
from mlspeclib.io import IO
from mlspeclib.helpers import convert_yaml_to_dict

from tests.sample_schemas import SampleSchema
from tests.sample_submissions import SampleSubmissions

class test_io(unittest.TestCase): #pylint: disable=invalid-name
    """io test cases."""
    def test_load_file_from_disk(self):
        all_objects = []

        for submission_file in list(Path('.').glob('tests/data/*.yaml')):
            all_objects.append(IO.get_object_from_path(submission_file))

if __name__ == '__main__':
    unittest.main()
