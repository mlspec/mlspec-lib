class SampleSchema:
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
    FULL = """
schema_version:
  # Identifies version of MLSpec to use
  type: semver
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

    FULL_SUBMITTED = """
schema_version: 0.0.1
run_id: f4bd7cee-42f9-4f29-a21e-3f78a9bad121
step_id: f4bd7cee-42f9-4f29-a21e-3f78a9bad121
run_date: 1970-01-01 00:00:00.00000"""
