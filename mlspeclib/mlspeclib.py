import os, sys
from pathlib import Path
import semver
from ruamel.yaml import YAML
from ruamel.yaml.compat import StringIO

class SchemaCollection:
    schemas = {}

    def __init__(self):
        pass

class Schema:
    _version = ""
    
    def __init__(self, version):
        _version = version

def load_all_schemas():
    yaml = YAML(typ='safe')
    # The below is extremely gross - fix
    all_schema_paths = list(Path("data").rglob("*.yaml"))
    print (all_schema_paths)
    for schema_path in all_schema_paths:
        with schema_path.open() as f: 
            print("Reading %s" % schema_path)
            content = f.read()
            schema_yaml = yaml.load(content)
            print(schema_yaml)
            
load_all_schemas()

