# -*- coding: utf-8 -*-
from . import helpers

import os, sys
from pathlib import Path
import semver
from ruamel.yaml import YAML
from ruamel.yaml.compat import StringIO
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
        yaml = YAML(typ='safe')
        print("Reading %s" % f.path)
        content = f.read()
        schema_type_yaml = yaml.load(content)
        print(schema_type_yaml)
        # schema = process_schema(schema_yaml)
        return True

    def process_schema_type(self, schema_yaml):
        # Confirm there is a version and that it snaps to SemVer
        try:
             SemVer(schema_yaml['schema_version'])
        except:
            raise
        # Confirm there are fields in the schema
        # Find the name of the schema (and special case base)
        # Confirm there isn't already a schema with this name & version combination in the schema collection
        # Build the schema object to insert into the collection
        # Pull out each field in the schema
            # Recurse for sub schemas - NOT SUPPORTED YET
            # Validate each field according to its validator
            # Attach the schema to the schema object


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