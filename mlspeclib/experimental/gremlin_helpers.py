import sys
import yaml
from pathlib import Path

sys.path.append("..")
sys.path.append("/home/daaronch-wsl/mlspeclib")

from mlspeclib.mlschema import MLSchema
from mlspeclib.mlschemaenums import MLSchemaTypes
from mlspeclib.mlobject import MLObject
from mlspeclib.helpers import return_schema_name, convert_yaml_to_dict
import tempfile

import json
import uuid
import logging

from gremlin_python import statics
from gremlin_python.structure.graph import Graph
from gremlin_python.process.graph_traversal import __
from gremlin_python.process.strategies import *
from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection
from gremlin_python.driver import client, serializer

import traceback

logging.basicConfig(level=logging.DEBUG)


class GremlinHelpers:
    _gremlin_cleanup_graph = "g.V().drop()"
    _gremlin_count_vertices = "g.V().count()"

    edges_to_submit = {}
    _url = None
    _key = None
    _database_name = None
    _container_name = None
    _workflow_id = None
    _gremlin_client = None
    _workflow_node_id = None

    def __init__(
        self,
        url=None,
        key=None,
        database_name=None,
        container_name=None,
        local_file: Path = None,
    ):
        if local_file is not None:
            settings_dict = convert_yaml_to_dict(local_file.read_text())
            url = settings_dict["url"]
            key = settings_dict["key"]
            database_name = settings_dict["database_name"]
            container_name = settings_dict["container_name"]

        self._url = url
        self._key = key
        self._database_name = database_name
        self._container_name = container_name

        self._workflow_id = uuid.uuid4()

        self._gremlin_client = client.Client(
            f"wss://{url}/",
            "g",
            username=f"/dbs/{database_name}/colls/{container_name}",
            password=f"{key}",
            message_serializer=serializer.GraphSONSerializersV2d0(),
        )

    def cleanup_graph(self):
        logging.debug(
            "\tRunning this Gremlin query:\n\t{0}".format(self._gremlin_cleanup_graph)
        )
        callback = self._gremlin_client.submitAsync(self._gremlin_cleanup_graph)
        if callback.result() is not None:
            logging.debug("\tCleaned up the graph!")

    def build_schema_name(self, workflow_step_object):
        return return_schema_name(
            workflow_step_object["schema_version"], workflow_step_object["schema_type"]
        )

    def create_workflow_node(self, schema_version):
        query = f"g.addV('workflow').property('id', '{schema_version}').property('workflow_id', '{self._workflow_id}')"
        returned_node = self.execute_query(query, True)
        self._workflow_node_id = returned_node["id"]

    def insert_vertex(
        self,
        step_name,
        in_schema,
        execution_schema,
        out_schema,
        workflow_id,
        previous_step=None,
        next_step=None,
    ):

        insert_query = f"""g.addV('step').property('id', '{step_name}')
                .property('in_schema', '{self.__build_schema_name(in_schema)}')
                .property('execution_schema', '{self.__build_schema_name(execution_schema)}')
                .property('out_schema', '{self.__build_schema_name(out_schema)}')
                .property('workflow_id', '{workflow_id}')"""

        self.edges_to_submit[step_name] = (previous_step, next_step)

        self.execute_query(insert_query)

        part_of_query = (
            f"g.V('{step_name}').addE('part_of').to(g.V('{self._workflow_node_id}'))"
        )
        logging.debug(f"Part_of_query: {part_of_query}")
        self.execute_query(part_of_query)

        contains_query = (
            f"g.V('{step_name}').addE('contains').from(g.V('{self._workflow_node_id}'))"
        )
        logging.debug(f"Contains_query: {contains_query}")
        self.execute_query(contains_query)

    def connect_workflow_steps(self):
        for edge in self.edges_to_submit:
            self.connect_vertices(
                edge, self.edges_to_submit[edge][0], self.edges_to_submit[edge][1]
            )

        self.edges_to_submit = {}

    def connect_vertices(self, step_name, previous_step, next_step):
        if previous_step is not None:
            previous_query = (
                f"g.V('{step_name}').addE('previous').from(g.V('{previous_step}'))"
            )
            self.execute_query(previous_query)

        if next_step is not None:
            next_query = f"g.V('{step_name}').addE('previous').from(g.V('{next_step}'))"
            self.execute_query(next_query)

    def execute_query(self, query, return_node=False):
        logging.debug(f"Inside the execute query: {query}")
        callback = self._gremlin_client.submitAsync(query)
        result = None
        if callback.result() is not None:
            result = callback.result().one()
            logging.debug("\tExecuted:\n\t{0}\n".format(result))
        else:
            logging.debug("Something went wrong with this query: {0}".format(query))

        if return_node:
            return result[0]

    def __build_schema_name(self, workflow_step_object):
        return return_schema_name(
            workflow_step_object["schema_version"], workflow_step_object["schema_type"]
        )

    def empty_graph(self):
        self.cleanup_graph()
