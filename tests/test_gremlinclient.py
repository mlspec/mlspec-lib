# pylint: disable=protected-access,missing-function-docstring, missing-class-docstring
# pylint: disable=missing-module-docstring, missing-class-docstring
# -*- coding: utf-8 -*-
import unittest
from pathlib import Path
import mock
from mock import patch, MagicMock
import sys
import yaml

from mlspeclib.mlschema import MLSchema
from mlspeclib.mlobject import MLObject
from mlspeclib.io import IO
from mlspeclib.experimental.gremlin_helpers import GremlinHelpers
from mlspeclib.experimental.metastore import Metastore
from mlspeclib import helpers
from mlspeclib.helpers import decode_raw_object_from_db


class GremlinHelpersTestSuite(unittest.TestCase):  # pylint: disable=invalid-name
    """io test cases."""

    @patch.object(GremlinHelpers, '__init__', return_value=None)
    @patch.object(MLObject, 'create_object_from_string', return_value=None)
    @patch.object(GremlinHelpers, 'execute_query', return_value=[{'properties': {'raw_content': [{'value': 'Zm9v'}]}}])
    def test_pass_through_workload_node_id(self, mock_gremlin_client_execute_query, mock_helpers, *other_mock_objects):
        ms = Metastore({})

        ms.get_workflow_object('FAKE_WORKFLOW_NODE_ID')

        call_args = GremlinHelpers.execute_query.call_args[0][0]
        self.assertTrue(call_args == "g.V('FAKE_WORKFLOW_NODE_ID')")

    @patch.object(yaml, 'safe_dump', return_value=None)
    @patch.object(GremlinHelpers, '__init__', return_value=None)
    @patch.object(MLObject, 'create_object_from_string', return_value=None)
    @patch.object(GremlinHelpers, 'execute_query', return_value=[{'properties': {'raw_content': [{'value': 'Zm9v'}]}}])
    def test_return_node_id_after_attach(self, mock_gremlin_client_execute_query, mock_helpers, *other_mock_objects):
        ms = Metastore({})
        mlobject = MagicMock()
        mlobject.run_id = 'FAKERUNID'
        mlobject.run_date = '1970-01-01T00:00:00'

        return_val = ms.attach_step_info(mlobject, '999.99.99', 'FAKE_NODE_ID', 'FAKE_STEP_NAME', 'input')

        self.assertTrue(return_val == 'FAKE_STEP_NAME|input|FAKERUNID|1970-01-01T00:00:00|999.99.99')


if __name__ == "__main__":
    unittest.main()
