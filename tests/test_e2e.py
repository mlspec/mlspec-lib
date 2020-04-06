# pylint: disable=protected-access,missing-function-docstring, missing-class-docstring, missing-module-docstring, missing-class-docstring
# -*- coding: utf-8 -*-
import unittest

from marshmallow import ValidationError

from mlspeclib.helpers import convert_yaml_to_dict

from mlspeclib.mlschema import MLSchema

from tests.sample_schemas import SampleSchema
from tests.sample_submissions import SampleSubmissions

class e2eTestSuite(unittest.TestCase): #pylint: disable=invalid-name
    """e2e test cases."""
    def test_load_full_base_schema(self):
        instantiated_schema = MLSchema.create(SampleSchema.SCHEMAS.BASE)
        submission_dict = convert_yaml_to_dict(SampleSubmissions.FULL_SUBMISSIONS.BASE)
        instantiated_object = instantiated_schema.load(submission_dict)
        assert instantiated_object['run_date'].isoformat() == \
               submission_dict['run_date'].isoformat()

        submission_dict.pop('run_date', None)
        with self.assertRaises(ValidationError):
            instantiated_schema.load(submission_dict)

    def test_load_full_datapath_schema(self):
        instantiated_schema = MLSchema.create(SampleSchema.SCHEMAS.DATAPATH)
        submission_dict = convert_yaml_to_dict(SampleSubmissions.FULL_SUBMISSIONS.DATAPATH)
        instantiated_object = instantiated_schema.load(submission_dict)
        assert instantiated_object['run_date'].isoformat() == \
               submission_dict['run_date'].isoformat()
        assert instantiated_object['connection']['endpoint'] == \
               submission_dict['connection']['endpoint']

        submission_dict.pop('run_date', None)
        with self.assertRaises(ValidationError):
            instantiated_schema.load(submission_dict)

if __name__ == '__main__':
    unittest.main()
