# pylint: disable=all
# flake8: noqa

""" Sample MLSchema used for testing. """


class SampleSchema:
    """ Sample schemas for testing - in two classes. TEST to for unittests, and
    SCHEMA for full e2e tests. """

    class TEST:
        """ TEST class of schemas for unittests. """
        STORAGE = """
storage_connection_type:
    type: string
    allowed:
        - 'AWS_BLOB', # AWS Blob"""

        UUID = """
run_id:
    type: uuid
    required: True
"""

        SEMVER = """
schema_version:
    type: semver
    required: True
"""

        DATETIME = """
run_date:
    type: datetime
    required: True
"""

        URI = """
endpoint:
    type: URI
    required: True
"""

        INVALID_YAML = """
a:
    - b
    % c"""

        ONE = """
qaz: a
quz: b"""

        TWO_THAT_REFERENCES_ONE = """
foo: 1
bar: 2
base_type: base"""

        REGEX = """
all_letters:
    type: string
    regex: '[a-zA-Z]+'"""

        INVALID_REGEX = """
all_letters:
    type: string
    regex: '['"""

        MLSPEC_SCHEMA_VERSION = """
mlspec_schema_version:
    # Identifies the version of this schema
    meta: 0.0.1
"""

        MLSPEC_SCHEMA_TYPE = """
mlspec_schema_type:
    # Identifies the type of this schema
    meta: base
"""
        INTERFACE = """
    inputs:
        type: list_interfaces
        required: True
"""
        WORKFLOW_STEP = """
        steps:
            type: workflow_steps
            required: True
"""
        OPERATOR_VALID = """
        num:
            type: int
            constraint: 'x >= 1000'
        """

        OPERATOR_VALID_MODULO_2 = """
        num:
            type: int
            constraint: 'x % 2 == 0'
        """

        OPERATOR_INVALID_TYPE = """
        num:
            type: string
            constraint: 'x >= 1000'
        """

        OPERATOR_INVALID_NO_OPERATOR = """
        num:
            type: int
            constraint: 'x 1000'
        """


    class SCHEMAS:
        """ SCHEMA class of test schemas pulled from real versions (as of 2020-04-04). """
        BASE = """
mlspec_schema_version:
    # Identifies the version of this schema
    meta: 0.0.1

mlspec_schema_type:
    # Base schema type that this extends
    meta: base

schema_version:
  # Identifies version of MLSpec to use
  type: semver
  required: True
schema_type:
  # Identifies version of MLSpec to use
  type: allowed_schema_types
  required: True
run_id:
  # Unique identifier for the execution of the entire workflow (designed to tie all steps together)
  type: uuid
  required: True
step_id:
  # Unique identifier for the execution of a step
  type: uuid
  required: True
run_date:
  # Execution datetime of a step in UTC
  type: datetime
  required: True
"""

        DATAPATH = """
mlspec_base_type:
    # Base schema type that this extends
    meta: base

mlspec_schema_version:
    # Identifies the version of this schema
    meta: 0.0.1

mlspec_schema_type:
    # Identifies the schema type of this schema
    meta: datapath

schema_version:
  # Identifies version of MLSpec to use to instantiate
  type: semver
  required: True

schema_type:
  # Identifies type of MLSpec to use to instantiate
  type: allowed_schema_types
  required: True

# Identifies name of datastore
data_store:
  type: string
  required: True
  empty: False

# Type of storage for the datastore, or CUSTOM for not present
storage_connection_type:
  type: string
  required: True
  allowed:
      - 'CUSTOM' # Custom connection
      - 'AWS_BLOB' # AWS Blob
      - 'GCP_BLOB' # Google Cloud Blob
      - 'AZURE_BLOB' # Azure Blob Storage
      - 'NFS_BLOB' # NFS Blob Storage
      - 'SMB_BLOB' # Samba Blob Storage

# Connection to datapath
connection:
  type: nested
  schema:
    # URI for the location of the data store
    endpoint:
        type: URI
        required: True

    # AWS access key (NOT RECOMMENDED - Use secret storage to provide connection)
    access_key_id:
        type: string
        regex: (?<![A-Z0-9])[A-Z0-9]{20}(?![A-Z0-9])

    # AWS access key (NOT RECOMMENDED - Use secret storage to provide connection)
    secret_access_key:
        type: string
        regex: (?<![A-Za-z0-9/+=])[A-Za-z0-9/+=]{40}(?![A-Za-z0-9/+=])"""
