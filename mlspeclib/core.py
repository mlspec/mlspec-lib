# -*- coding: utf-8 -*-
from . import helpers

import os, sys
from pathlib import Path
import semver
import strictyaml
import mlspeclib.schemavalidator as SchemaValidator
import cerberus

class PopulateRegistry(object):

    sample_schema = '''
schema_version:
  # Identifies version of MLSpec to use
  type: semver
  required: true
run_id: 
  # Unique identifier for the execution of the entire workflow (designed to tie all steps together)
  type: uuid
  required: true
step_id:
  # Unique identifier for the execution of a step
  type: uuid
  required: true
run_date:
  # Execution datetime of a step in UTC
  type: datetime
  required: true
    '''

    def __init__(self):
        pass

    def load_all_schemas(self):
        # The below is extremely gross - fix
        all_schema_type_paths = list(Path("data").rglob("*.yaml"))
        print (all_schema_type_paths)
        for schema_type_path in all_schema_type_paths:
            with schema_type_path.open() as f: 
                print("foo")
                # schema_type_yaml = self.read_schema_type(f)
                # schema = process_schema(schema_yaml)
        return self

    def read_schema_type(self, f):
        print("Reading %s" % f.path)
        content = f.read()
        schema_type_yaml = strictyaml.load(content)
        print(schema_type_yaml)
        # schema = process_schema(schema_yaml)
        return True

'''
    def process_schema_type(self, schema_yaml):
        # TODO: Check to see if schema_type is invalid somehow (just load it at let cerberus figure it out?)
        s = SchemaValidator()

        schema_text = """
schema_version:
  # Identifies version of MLSpec to use
  type: semver
  required: true
run_id: 
  # Unique identifier for the execution of the entire workflow (designed to tie all steps together)
  type: uuid
  required: true
step_id:
  # Unique identifier for the execution of a step
  type: uuid
  required: true
run_date:
  # Execution datetime of a step in UTC
  type: datetime
  required: true"""

        s.schema = strictyaml.load(schema_text)

        submitted_schema = """
schema_version: 0.0.1
run_id: f4bd7cee-42f9-4f29-a21e-3f78a9bad121
step_id: f4bd7cee-42f9-4f29-a21e-3f78a9bad121
run_date: 1970-01-01 00:00:00.00000"""

        s.validate(strictyaml.load(submitted_schema))

        # Figure out what type this schema is (by filename?)

        # Load base schema
        # Extend base schema with type specific schema

        # Attach schema to registry - ensure we can index by both schema version and type
        # TODO: Make sure we don't overwrite existing schema?
        # TODO: Is there a way to serialize the registry so we don't have to load this in every time?
        1
'''

if __name__ == '__main__':
    pr = PopulateRegistry()
    pr.load_all_schemas()

'''
schema_version: 0.0.1\nfields:\n  schema_version:\n    type: semver\n    description: Identifies version of MLSpec to use\n    required: true\n  run_id: \n    type: uuid\n    description: Unique identifier for the execution of the entire workflow (designed to tie all steps together)\n    required: true\n  step_id:\n    type: uuid\n    description: Unique identifier for the execution of a step\n    required: true\n  run_date:\n    type: datetime\n    description: Execution datetime of a step in UTC\n    required: true\n
'''

'''
{'schema_version': '0.0.1', 'fields': {'schema_version': {'type': 'semver', 'required': True}, 'run_id': {'type': 'uuid', 'required': True}, 'step_id': {'type': 'uuid', 'required': True}, 'run_date': {'type': 'datetime', 'required': True}}}
'''

'''
schema_version:
  # Identifies version of MLSpec to use
  type: semver
  required: true
run_id: 
  # Unique identifier for the execution of the entire workflow (designed to tie all steps together)
  type: uuid
  required: true
step_id:
  # Unique identifier for the execution of a step
  type: uuid
  required: true
run_date:
  # Execution datetime of a step in UTC
  type: datetime
  required: true
'''