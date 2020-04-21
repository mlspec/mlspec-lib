""" All allowed schema types as enums."""
from enum import Enum, auto

# TODO: Name spacing across schema - path to the definition library
# (folder than just has a list of definitions)
# User experience is at the top of a notebook say "mlspeclib.add_schema_registry(file_path)"
# TODO: Hierarchy of name lookups - two schema registries, need to start with root and cascade down
# - can reorder in lookup in schema registry


# TODO: Build this dynamically (maybe?) from files in mlspeclib/data
class MLSchemaTypes(Enum):
    """ Types of allowed schemas, the numbers don't matter so we populated them
    using auto()."""
    BASE = auto()
    DATAPATH = auto()
    ENVIRONMENT = auto()
    CONTAINERSTORE = auto()
    CONVERSION = auto()
    DATASCHEMA = auto()
    DATASOURCE = auto()
    METADATA = auto()
    SCORE = auto()
    SERVE = auto()
    TRAIN_EXECUTION = auto()
    TRAIN_RESULTS = auto()
    TRAINING_POST_PROCESS = auto()
    RUNCONFIG = auto()
    MODEL = auto()
    JOB = auto()
    COMPONENT = auto()
