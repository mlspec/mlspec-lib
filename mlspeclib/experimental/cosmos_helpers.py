import sys
import yaml
from pathlib import Path

sys.path.append("..")
sys.path.append(Path(__file__).parent.resolve())

from mlspeclib.mlschema import MLSchema
from mlspeclib.mlschemaenums import MLSchemaTypes
from mlspeclib.mlobject import MLObject
from mlspeclib.helpers import return_schema_name, convert_yaml_to_dict
import tempfile

import json
import uuid
import logging

from azure.cosmos import exceptions, CosmosClient, PartitionKey
import traceback

logging.basicConfig(level=logging.DEBUG)

class CosmosHelpers:
    edges_to_submit = {}
    _url = None
    _key = None
    _database_name = None
    _container_name = None
    _workflow_partition_id = None
    _cosmos_client = None
    _database_client = None
    _workflow_node_id = None

    def __init__(
        self,
        url=None,
        key=None,
        database_name=None,
        container_name=None,
        credential_dict: str = None,
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

        self._workflow_id = uuid.uuid4()

        self._cosmos_client = CosmosClient(self._url, self._key)
        self._db_client = self._cosmos_client.get_database_client(f"/dbs/{database_name}")
        self._container_client = self._db_client.get_container_client(f"/colls/{container_name}")

    # def cleanup_graph(self):
    #     logging.debug(
    #         "\tRunning this Gremlin query:\n\t{0}".format(self._gremlin_cleanup_graph)
    #     )
    #     callback = self._gremlin_client.submitAsync(self._gremlin_cleanup_graph)
    #     if callback.result() is not None:
    #         logging.debug("\tCleaned up the graph!")

    # def build_schema_name(self, workflow_step_object):
    #     return return_schema_name(
    #         workflow_step_object["schema_version"], workflow_step_object["schema_type"]
    #     )

    # def create_workflow_node(self, schema_version):
    #     query = f"g.addV('workflow').property('id', '{schema_version}').property('workflow_id', '{self._workflow_id}')"
    #     returned_node = self.execute_query(query, True)
    #     self._workflow_node_id = returned_node["id"]

    # def insert_vertex(
    #     self,
    #     step_name,
    #     in_schema,
    #     execution_schema,
    #     out_schema,
    #     workflow_id,
    #     previous_step=None,
    #     next_step=None,
    # ):

    #     insert_query = f"""g.addV('step').property('id', '{step_name}')
    #             .property('in_schema', '{self.__build_schema_name(in_schema)}')
    #             .property('execution_schema', '{self.__build_schema_name(execution_schema)}')
    #             .property('out_schema', '{self.__build_schema_name(out_schema)}')
    #             .property('workflow_id', '{workflow_id}')"""

    #     self.edges_to_submit[step_name] = (previous_step, next_step)

    #     self.execute_query(insert_query)

    #     part_of_query = (
    #         f"g.V('{step_name}').addE('part_of').to(g.V('{self._workflow_node_id}'))"
    #     )
    #     logging.debug(f"Part_of_query: {part_of_query}")
    #     self.execute_query(part_of_query)

    #     contains_query = (
    #         f"g.V('{step_name}').addE('contains').from(g.V('{self._workflow_node_id}'))"
    #     )
    #     logging.debug(f"Contains_query: {contains_query}")
    #     self.execute_query(contains_query)

    # def attach_step_info(
    #     self, mlobject: MLObject, workflow_id, step_name: str, step_type: str
    # ):
    #     if step_type not in ["input", "execution", "output"]:
    #         raise ValueError(
    #             f"Error when saving '{mlobject.get_schema_name()}', the content_type must be from ['input', 'execution', 'output']."
    #         )
    #     run_info_id = f"{step_name}|{mlobject.run_id}|{mlobject.run_date}"
    #     add_run_info_query = f"""g.addV('step_run').property('id', '{run_info_id}')
    #                         .property('run_id', '{mlobject.run_id}')
    #                         .property('run_date', '{mlobject.run_date}')
    #                         .property('{step_type}_content', '{mlobject.to_yaml()}')"""

    #     self.execute_query(add_run_info_query)

    #     self.execute_query(
    #         f"g.V('{self._workflow_node_id}').out().hasId({step_name}).addE('results').to(g.V('{run_info_id}'))"
    #     )
    #     self.execute_query(
    #         f"g.V('{self._workflow_node_id}').out().hasId({step_name}).addE('root').from(g.V('{run_info_id}'))"
    #     )

    # def connect_workflow_steps(self):
    #     for edge in self.edges_to_submit:
    #         self.connect_vertices(
    #             edge, self.edges_to_submit[edge][0], self.edges_to_submit[edge][1]
    #         )

    #     self.edges_to_submit = {}

    # def connect_next_previous_vertices(self, step_name, previous_step, next_step):
    #     if previous_step is not None:
    #         previous_query = (
    #             f"g.V('{step_name}').addE('previous').from(g.V('{previous_step}'))"
    #         )
    #         self.execute_query(previous_query)

    #     if next_step is not None:
    #         next_query = f"g.V('{step_name}').addE('previous').from(g.V('{next_step}'))"
    #         self.execute_query(next_query)

    # def execute_query(self, query, return_node=False):
    #     logging.debug(f"Inside the execute query: {query}")

    #     # TODO: Need to implement sanitization.
    #     logging.warn(
    #         f"*** execute_query DOES NO SANITIZATION OF INPUTS. BE EXTREMELY CAREFUL. ***"
    #     )
    #     callback = self._gremlin_client.submitAsync(query)
    #     result = None
    #     if callback.result() is not None:
    #         result = callback.result().one()
    #         logging.debug("\tExecuted:\n\t{0}\n".format(result))
    #     else:
    #         logging.debug("Something went wrong with this query: {0}".format(query))

    #     if return_node:
    #         return result[0]

    # def __build_schema_name(self, workflow_step_object):
    #     return return_schema_name(
    #         workflow_step_object["schema_version"], workflow_step_object["schema_type"]
    #     )

    # def empty_graph(self):
    #     self.cleanup_graph()
