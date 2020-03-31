class SampleSubmissions:
    BASE = """
schema_version: 0.0.1
schema_type: base
run_id: f4bd7cee-42f9-4f29-a21e-3f78a9bad121
step_id: c84305d1-fe42-48df-9b47-f7628172ac1d
run_date: 1970-01-01 00:00:00.00000"""

    DATAPATH = """
schema_version: 0.0.1
schema_type: datapath
base_type: base
run_id: 6a9a5931-1c1d-47cc-aaf3-ad8b03f70575
step_id: 0c98f080-4760-46be-b35f-7dbb5e2a88c2
run_date: 1970-01-01 00:00:00.00000
data_store: I_am_a_datastore_name
storage_connection_type: AWS_BLOB
connection:
    endpoint: S3://mybucket/puppy.jpg
    access_key_id: AKIAIOSFODNN7EXAMPLE
    secret_access_key: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"""