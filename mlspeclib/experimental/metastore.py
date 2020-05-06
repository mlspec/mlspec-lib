import sys
import yaml
from pathlib import Path

from mlspeclib.mlschema import MLSchema
from mlspeclib.mlschemaenums import MLSchemaTypes
from mlspeclib.mlobject import MLObject
from mlspeclib.helpers import return_schema_name, convert_yaml_to_dict
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
