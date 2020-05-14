import sys
import yaml
from pathlib import Path

from mlspeclib.mlschema import MLSchema
from mlspeclib.mlschemaenums import MLSchemaTypes
from mlspeclib.mlobject import MLObject
from mlspeclib.helpers import (
    return_schema_name,
    convert_yaml_to_dict,
    decode_raw_object_from_db,
)
from mlspeclib.experimental.gremlin_helpers import GremlinHelpers
import tempfile

import json
import uuid

import traceback

import logging


class Metastore:
    _gc = None

    def __init__(self, credentials):
        self._gc = GremlinHelpers(credential_dict=credentials)

    def save(self, mlobject: MLObject, workflow_version_id, step_name, content_type):
        """ Saves an MLObject to the metastore connection. Uses the run_id from the object,
        and attaches all non-internal fields on the MLObject as properties, as well as storing
        an encoded representation of the full yaml under raw_content.

        Also creates edges with the specific step as:
            step_name -> .out('result') -> mlobject
            mlobject -> .out('root') -> step_name"""

        self._gc.attach_step_info(
            mlobject, workflow_version_id, step_name, content_type
        )

    def get_all_runs(self, workflow_version_id, step_name):
        return self._gc.get_all_runs(workflow_version_id, step_name)

    def load(self, workflow_version, step_name, run_info_id):
        return self._gc.get_run_info(workflow_version, step_name, run_info_id)

    def get_workflow_object(self, workflow_version_id):
        full_results = self._gc.get_workflow_node(workflow_version_id)
        if len(full_results) == 0:
            return None
        elif len(full_results) > 1:
            logging.debug(
                "More than one workflow associated with this schema. Returning None."
            )
            return None
        else:
            raw_item = full_results[0]

        if (
            "properties" not in raw_item
            or "raw_content" not in raw_item["properties"]
            or len(raw_item["properties"]["raw_content"]) == 0
            or "value" not in raw_item["properties"]["raw_content"][0]
        ):
            return None

        obf_string = raw_item["properties"]["raw_content"][0]["value"]
        return MLObject.create_object_from_string(decode_raw_object_from_db(obf_string))

    def get_step_object(self, workflow_version_id, step_name, run_info_id):
        raw_item = self.load(workflow_version_id, step_name, run_info_id)

        if (
            "properties" not in raw_item
            or "raw_content" not in raw_item["properties"]
            or len(raw_item["properties"]["raw_content"]) == 0
            or "value" not in raw_item["properties"]["raw_content"][0]
        ):
            return None

        obf_string = raw_item["properties"]["raw_content"][0]["value"]
        return MLObject.create_object_from_string(decode_raw_object_from_db(obf_string))

    def empty_graph(self):
        return self._gc.empty_graph()

    def create_workflow_node(self, workflow_object: MLObject):
        return self._gc.create_workflow_node(
            workflow_object.get_schema_version(), workflow_object
        )

    def create_workflow_steps(self, raw_workflow_node, workflow_object: MLObject):
        edges_to_submit = {}
        for step_name in workflow_object.steps:
            step_contents = workflow_object.steps[step_name]

            next_step = None
            previous_step = None
            if "previous" in step_contents:
                previous_step = step_contents.previous
            if "next" in step_contents:
                next_step = step_contents.next

            step_name = step_name
            input_schema_version = step_contents.input.schema_version
            input_schema_type = step_contents.input.schema_type
            execution_schema_version = step_contents.execution.schema_version
            execution_schema_type = step_contents.execution.schema_type
            output_schema_version = step_contents.output.schema_version
            output_schema_type = step_contents.output.schema_type

            workflow_version_id = raw_workflow_node[0]["properties"]["version"][0][
                "value"
            ]
            previous_step = previous_step
            next_step = next_step

            edges_to_submit[step_name] = (previous_step, next_step)

            self._gc.insert_workflow_step(
                step_name=step_name,
                input_schema_version=input_schema_version,
                input_schema_type=input_schema_type,
                execution_schema_version=execution_schema_version,
                execution_schema_type=execution_schema_type,
                output_schema_version=output_schema_version,
                output_schema_type=output_schema_type,
                workflow_version_id=workflow_version_id,
                previous_step=previous_step,
                next_step=next_step,
            )

        self._gc.connect_workflow_steps(edges_to_submit)

    def execute_query(self, query):
        """ Executes arbitrary query. Be careful. """
        return self._gc.execute_query(query)
