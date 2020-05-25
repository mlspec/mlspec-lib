# pylint: disable=protected-access,missing-function-docstring, missing-class-docstring
# pylint: disable=missing-module-docstring, missing-class-docstring
# -*- coding: utf-8 -*-
import unittest
from pathlib import Path
import mock
from mock import patch, MagicMock
import sys
import yaml
import pymysql
import logging
from logging import RootLogger

sys.path.append(str(Path.cwd()))
sys.path.append(str(Path.cwd().parent))

from mlspeclib.mlschema import MLSchema
from mlspeclib.mlobject import MLObject
from mlspeclib.io import IO
from mlspeclib.experimental.gremlin_helpers import GremlinHelpers
from mlspeclib.experimental.metastore import Metastore
from mlspeclib import helpers
from mlspeclib.helpers import decode_raw_object_from_db


class GremlinHelpersTestSuite(unittest.TestCase):  # pylint: disable=invalid-name
    """io test cases."""

    @patch.object(GremlinHelpers, "__init__", return_value=None)
    @patch.object(MLObject, "create_object_from_string", return_value=None)
    @patch.object(
        GremlinHelpers,
        "execute_query",
        return_value=[{"properties": {"raw_content": [{"value": "Zm9v"}]}}],
    )
    def test_pass_through_workload_node_id(
        self, mock_gremlin_client_execute_query, mock_helpers, *other_mock_objects
    ):
        ms = Metastore({})

        ms.get_workflow_object("FAKE_WORKFLOW_NODE_ID")

        call_args = GremlinHelpers.execute_query.call_args[0][0]
        self.assertTrue(call_args == "g.V('FAKE_WORKFLOW_NODE_ID')")

    @patch.object(yaml, "safe_dump", return_value=None)
    @patch.object(GremlinHelpers, "__init__", return_value=None)
    @patch.object(MLObject, "create_object_from_string", return_value=None)
    @patch.object(
        GremlinHelpers,
        "execute_query",
        return_value=[{"properties": {"raw_content": [{"value": "Zm9v"}]}}],
    )
    def test_return_node_id_after_attach(
        self, mock_gremlin_client_execute_query, mock_helpers, *other_mock_objects
    ):
        ms = Metastore({})
        mlobject = MagicMock()
        mlobject.run_id = "FAKERUNID"
        mlobject.run_date = "1970-01-01T00:00:00"

        return_val = ms.attach_step_info(
            mlobject, "999.99.99", "FAKE_NODE_ID", "FAKE_STEP_NAME", "input"
        )

        self.assertTrue(
            return_val == "FAKE_STEP_NAME|input|FAKERUNID|1970-01-01T00:00:00|999.99.99"
        )

    @patch.object(yaml, "safe_dump", return_value=None)
    @patch.object(GremlinHelpers, "__init__", return_value=None)
    @patch.object(MLObject, "create_object_from_string", return_value=None)
    @patch.object(GremlinHelpers, "_rootLogger")
    @patch.object(pymysql, "escape_string", return_val="")
    @patch.object(
        GremlinHelpers,
        "execute_query",
        return_value=[{"properties": {"raw_content": [{"value": "Zm9v"}]}}],
    )
    def test_create_workflow_node(
        self,
        mock_gremlin_client_execute_query,
        mock_helpers,
        mock_logger,
        *other_mock_objects,
    ):
        ms = Metastore({})

        mock_logger.debug.return_value = None

        workflow_object = MagicMock()
        workflow_object.workflow_version = "9999.9999.9999"
        workflow_partition_id = "f7f07502-d099-49fd-a072-d1396a2e40a0"
        workflow_node_id = ms.create_workflow_node(
            workflow_object, workflow_partition_id
        )

        self.assertTrue(
            workflow_node_id
            == f"workflow|workflow|{workflow_object.workflow_version}|{workflow_partition_id}"
        )


if __name__ == "__main__":
    unittest.main()
