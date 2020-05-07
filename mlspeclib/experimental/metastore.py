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


class Metastore:
    _gc = None

    def __init__(self, credentials):
        self._gc = GremlinHelpers(credential_dict=credentials)

    def save(self, mlobject: MLObject, workflow_id, step_name, content_type):
        self._gc.attach_step_info(mlobject, workflow_id, step_name, content_type)

    def get_all_runs(self, workflow_id, step_name):
        return self._gc.get_all_runs(workflow_id, step_name)

    def load(self, workflow_id, step_name, run_info_id):
        return self._gc.get_run_info(workflow_id, step_name, run_info_id)

    def get_ml_object(self, workflow_id, step_name, run_info_id):
        raw_item = self.load("0.0.1", "process_data", run_info_id)

        if (
            "properties" not in raw_item
            or "raw_content" not in raw_item['properties']
            or len(raw_item["properties"]["raw_content"]) == 0
            or "value" not in raw_item["properties"]["raw_content"][0]
        ):
            return None

        obf_string = raw_item["properties"]["raw_content"][0]["value"]
        return MLObject.create_object_from_string(decode_raw_object_from_db(obf_string))
