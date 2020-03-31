class SampleSchema:
    class TEST:
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



    class SCHEMAS:
        BASE = """
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
    required: True"""

        DATAPATH = """
schema_version:
    # Identifies version of MLSpec to use
    type: semver
    required: True

schema_type:
  # Identifies version of MLSpec to use
  type: allowed_schema_types
  required: True  

base_type:
    # Base schema type that this extends
    meta: base

# Identifies name of datastore
data_store:
  type: string
  required: True

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
  type: 'dict'
  schema: 
    # URI for the location of the data store
    endpoint:
        type: URI
        required: True
    # AWS access key (NOT RECOMMENDED - Use secret storage to provide connection)
    access_key_id:
        type: string
        regex: (?<![A-Z0-9])[A-Z0-9]{20}(?![A-Z0-9])
    secret_access_key:
        type: string
        regex: (?<![A-Za-z0-9/+=])[A-Za-z0-9/+=]{40}(?![A-Za-z0-9/+=])"""
