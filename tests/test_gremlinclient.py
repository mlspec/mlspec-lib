# pylint: disable=protected-access,missing-function-docstring, missing-class-docstring
# pylint: disable=missing-module-docstring, missing-class-docstring
# -*- coding: utf-8 -*-
import unittest
from pathlib import Path
import mock
from mock import patch
import sys

sys.path.append(str(Path().parent))

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
    @patch.object(GremlinHelpers, 'execute_query', return_value=[{'properties':{'raw_content':[{'value': 'Zm9v'}]}}])
    def test_pass_through_workload_node_id(self, mock_gremlin_client_execute_query, mock_helpers, *other_mock_objects):
        ms = Metastore({})

        ms.get_workflow_object('FAKE_WORKFLOW_NODE_ID')

        call_args = GremlinHelpers.execute_query.call_args[0][0]
        self.assertTrue(call_args == "g.V('FAKE_WORKFLOW_NODE_ID')")

if __name__ == "__main__":
    unittest.main()
