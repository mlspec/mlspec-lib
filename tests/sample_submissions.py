# pylint: disable=invalid-name, missing-class-docstring, too-few-public-methods
""" Sample Submissions for test cases. """
class SampleSubmissions:
    """ Static submissions for test cases - BASE and DATAPATH (which references BASE) """

    class UNIT_TESTS:
        STORAGE_VALID = "storage_connection_type: 'AWS_BLOB'"
        STORAGE_INVALID = "storage_connection_type: 'xxxx'"
        UUID_VALID = "run_id: 'a04bf86c-90bc-4869-8851-b200c7ad3ccd'"

        # Contains an 'x'
        UUID_INVALID = "run_id: 'a0xbf86c-90bc-4869-8851-b200c7ad3ccd'"
        SEMVER_VALID = "0.0.1"
        SEMVER_INVALID = "0.0.x"
        DATETIME_VALID = "run_date: 1970-01-01 00:00:00"
        DATETIME_INVALID = "run_date: xxxx"
        URI_VALID_1 = "endpoint: 'https://s3.us-west-2.amazonaws.com/mybucket/puppy.jpg'"
        URI_VALID_2 = "endpoint: 'S3://mybucket/puppy.jpg'"
        URI_INVALID_1 = "endpoint: xxx"
        URI_INVALID_2 = "endpoint: 123"
        INVALID_YAML = """
    a:
        - b
        % c"""
        REGEX_ALL_LETTERS = "all_letters: abcde"
        REGEX_ALL_NUMBERS = "all_letters: '129381'"

    class FULL_SUBMISSIONS:
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