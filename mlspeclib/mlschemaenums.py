""" All allowed schema types as enums."""
from enum import Enum, auto


# TODO: Build this dynamically (maybe?) from files in mlspeclib/data
class MLSchemaTypes(Enum):
    """ Types of allowed schemas, the numbers don't matter so we populated them
    using auto()."""
    BASE = auto()
    DATAPATH = auto()
    ENVIRONMENT = auto()
    CONTAINER_STORE = auto()
    CONVERSION = auto()
    DATA_SCHEMA_LOCATIONS = auto()
