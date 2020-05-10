import sys
import yaml
from pathlib import Path

from mlspeclib.mlschema import MLSchema
from mlspeclib.mlschemaenums import MLSchemaTypes
from mlspeclib.mlobject import MLObject
from mlspeclib.helpers import (
    return_schema_name,
    convert_yaml_to_dict,
    to_yaml,
    to_json,
    encode_raw_object_for_db,
)
from collections import OrderedDict
import tempfile

import json
import uuid
import logging

from gremlin_python import statics
from gremlin_python.structure.graph import Graph
from gremlin_python.process.graph_traversal import __
from gremlin_python.process.strategies import *
from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection
from gremlin_python.driver import client, serializer, resultset

import asyncio

import pymysql

import traceback

import tornado

sys.path.append("..")
sys.path.append(Path(__file__).parent.resolve())


class GremlinHelpers:
    _gremlin_cleanup_graph = "g.V().drop()"
    # _gremlin_cleanup_graph = ""
    _gremlin_count_vertices = "g.V().count()"

    _url = None
    _key = None
    _database_name = None
    _container_name = None
    _workflow_partition_id = None
    _gremlin_client = None
    _workflow_node_id = None
    _request = None
    _driver_remote_connection = None
    _graph = None

    def __init__(
        self,
        url=None,
        key=None,
        database_name=None,
        container_name=None,
        credential_dict: dict = None,
    ):
        if credential_dict is not None:
            url = credential_dict["url"]
            key = credential_dict["key"]
            database_name = credential_dict["database_name"]
            container_name = credential_dict["container_name"]

        self._url = url
        self._key = key
        self._database_name = database_name
        self._container_name = container_name

        self._workflow_partition_id = uuid.uuid4()

        print(self._url)
        self._gremlin_client = client.Client(
            f"{self._url}",
            "g",
            username=f"/dbs/{self._database_name}/colls/{self._container_name}",
            password=f"{self._key}",
            message_serializer=serializer.GraphSONSerializersV2d0(),
        )
        # self._request = httpclient.HTTPRequest(f"{self._url}", headers={"Authorization": "Token AZX ..."})
        # self._driver_remote_connection = DriverRemoteConnection(self._request.url, 'g', username=f"/dbs/{self._database_name}/colls/{self._container_name}", password=f"{self._key}",message_serializer=serializer.GraphSONSerializersV2d0())
        # self._graph = Graph()
        # self._g = self._graph.traversal().withRemote(self._driver_remote_connection, 'g')

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

    def create_workflow_node(self, workflow_version, mlobject):
        # mlobject_dict = mlobject.dict_without_internal_variables()
        # property_string = convert_to_property_strings(mlobject_dict)
        raw_content = encode_raw_object_for_db(mlobject)
        save_workflow_query = f"g.addV('id', 'workflow').property('version', '{workflow_version}').property('workflow_partition_id', '{self._workflow_partition_id}').property('raw_content', '{raw_content}')"

        return self.execute_query(save_workflow_query)

    def get_workflow_node(self, schema_version):
        query = "g.V().has('id', 'workflow').has('version', '%s')"
        return self.execute_query(sQuery(query, [schema_version]))

    def insert_workflow_step(
        self,
        step_name,
        input_schema_version,
        input_schema_type,
        execution_schema_version,
        execution_schema_type,
        output_schema_version,
        output_schema_type,
        workflow_version_id,
        previous_step=None,
        next_step=None,
    ):

        params = [
            step_name,
            input_schema_version,
            input_schema_type,
            execution_schema_version,
            execution_schema_type,
            output_schema_version,
            output_schema_type,
            workflow_version_id,
            str(self._workflow_partition_id),
        ]

        insert_query = sQuery(
            f"""g.addV('id','%s').property('type', 'workflow_step').property('input_schema_version', '%s').property('input_schema_type', '%s').property('execution_schema_version', '%s').property('execution_schema_type', '%s').property('output_schema_version', '%s').property('output_schema_type', '%s').property('workflow_version_id', '%s').property('workflow_partition_id', '%s')""",
            params,
        )

        self.execute_query(insert_query)

        part_of_query = f"g.V('{step_name}').addE('part_of').to(g.V().has('id', 'workflow').has('version', '{workflow_version_id}'))"
        logging.debug(f"Part_of_query: {part_of_query}")
        self.execute_query(part_of_query)

        contains_query = f"g.V('{step_name}').addE('contains').from(g.V().has('id', 'workflow').has('version', '{workflow_version_id}'))"
        logging.debug(f"Contains_query: {contains_query}")
        self.execute_query(contains_query)

    def attach_step_info(
        self, mlobject: MLObject, workflow_version_id, step_name: str, step_type: str
    ):
        if step_type not in ["input", "execution", "output", "log"]:
            raise ValueError(
                f"Error when saving '{mlobject.get_schema_name()}', the step_type must be from ['input', 'execution', 'output', 'log']."
            )
        run_info_id = get_run_info_id(step_name, mlobject.run_id, mlobject.run_date)
        mlobject_dict = mlobject.dict_without_internal_variables()
        property_string = convert_to_property_strings(mlobject_dict)
        raw_content = encode_raw_object_for_db(mlobject)
        add_run_info_query = f"""g.addV('id', '{run_info_id}'){property_string}.property('raw_content', '{raw_content}').property('workflow_partition_id', '{self._workflow_partition_id}')"""

        self.execute_query(add_run_info_query)

        self.execute_query(
            sQuery(
                "g.V('id', 'workflow').has('version', '%s').out().hasId('%s').addE('results').to(g.V('%s')).executionProfile()",
                [workflow_version_id, step_name, run_info_id],
            )
        )
        self.execute_query(
            sQuery(
                "g.V('id', 'workflow').has('version', '%s').out().hasId('%s').addE('root').from(g.V('%s')).executionProfile()",
                [workflow_version_id, step_name, run_info_id],
            )
        )

    def connect_workflow_steps(self, edges_to_submit):
        for edge in edges_to_submit:
            self.connect_next_previous_vertices(
                edge, edges_to_submit[edge][0], edges_to_submit[edge][1]
            )

    def connect_next_previous_vertices(self, step_name, previous_step, next_step):
        if previous_step is not None:
            previous_query = sQuery(
                f"g.V('%s').addE('previous').from(g.V('%s'))",
                [step_name, previous_step],
            )
            self.execute_query(previous_query)

        if next_step is not None:
            next_query = sQuery(
                f"g.V('%s').addE('next').to(g.V('%s'))", [step_name, next_step]
            )

            self.execute_query(next_query)

    def execute_query(self, query):
        logging.debug(f"Inside the execute query: {query}")

        # TODO: Need to implement sanitization.
        logging.warn(
            f"*** execute_query DOES NO SANITIZATION OF INPUTS. BE EXTREMELY CAREFUL. ***"
        )
        callback = self._gremlin_client.submitAsync(query)
        collected_result = []
        try:
            if callback.result() is not None:
                while True:
                    result_set = callback.result()
                    for result in result_set:
                        collected_result.extend(result)

                    if callback.done():
                        break

                    loop_sleep()

                logging.debug("\tExecuted:\n\t{0}\n".format(collected_result))
        except tornado.iostream.StreamClosedError as sce:
            logging.debug("Something went wrong with this query: {0}".format(query))
            logging.debug(f"Full error here: {str(sce)}")

        if len(collected_result) == 0:
            raise Exception(msg="Query returned zero results.")

        return collected_result

    def get_all_runs(
        self, workflow_version_id, step_name, descending_order=True
    ) -> list:
        order = "decr"
        if not descending_order:
            order = "incr"

        query = "g.V('id','workflow').has('version', '%s').out().has('id', '%s').out('results').order().by('run_date', %s)"

        results = self.execute_query(
            sQuery(query, [workflow_version_id, step_name, order])
        )

        result_dict = OrderedDict()
        for result in results:
            result_dict[result["id"]] = result

        return result_dict

    def get_run_info(self, workflow_version_id, step_name, run_info_id) -> dict:
        all_results = self.get_all_runs(
            workflow_version_id=workflow_version_id, step_name=step_name
        )
        if len(all_results) > 0:
            return all_results[run_info_id]
        else:
            return None

    def __build_schema_name(self, workflow_step_object):
        return return_schema_name(
            workflow_step_object["schema_version"], workflow_step_object["schema_type"]
        )

    def empty_graph(self):
        self.cleanup_graph()


async def loop_sleep():
    await asyncio.sleep(0.2)


def convert_to_property_strings(this_dict: dict, prefix=None):
    return_string = ""
    for key in this_dict:
        if isinstance(this_dict[key], dict):
            convert_to_property_strings(this_dict[key], prefix=key)

        key_string = str(key)

        if prefix is not None:
            key_string = f"{prefix}.{key_string}"

        return_string += f".property('{pymysql.escape_string(key_string)}', '{pymysql.escape_string(str(this_dict[key]))}')"
        # return_string += f".property({MySQLdb.escape_string(key_string,'utf-8')}, {MySQLdb.escape_string(str(this_dict[key]),'utf-8')})"

    return return_string


def sQuery(query, parameters: list = []):
    num_of_params = query.count("%s")
    if len(parameters) != num_of_params:
        raise ValueError(
            f"Number of parameters ({num_of_params}) for query '{query}' not equal to parameters. Parameters given: {parameters}"
        )

    safe_parameters = []
    for param in parameters:
        safe_parameters.append(pymysql.escape_string(param))

    return query % tuple(safe_parameters)


def get_run_info_id(step_name, run_id, run_date):
    return f"{step_name}|{run_id}|{run_date}"
