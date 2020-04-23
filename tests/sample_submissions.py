# pylint: disable=invalid-name, missing-class-docstring, too-few-public-methods
# flake8: noqa

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

        INTERFACE_VALID_NAMED = """
            inputs:
                - columns:
                    name: training_set_columns
                    type: Integer
                    description: 'Number of columns on the input data set.'
                    default: 10
                - classes:
                    name: number_of_classes
                    type: Integer
                    description: 'Number of classifiers.'
                    default: 10
        """

        INTERFACE_VALID_UNNAMED = """
            inputs:
                - { name: training_set_columns, type: Integer, description: 'Number of columns on the input data set.', default: 10}
                - { name: number_of_classes, type: Integer, description: 'Number of classifiers.', default: 10}
        """

        INTERFACE_INVALID_MISSING_TYPE = """
            inputs:
                - columns:
                    name: training_set_columns
                    # type: Integer
                    description: 'Number of columns on the input data set.'
                    default: 10
        """

        INTERFACE_INVALID_MISMATCH_TYPE = """
            inputs:
                - columns:
                    name: number_of_classes
                    type: Integer
                    description: 'Number of classifiers.'
                    default: 'aeosuthao'
        """

        INTERFACE_INVALID_TYPE_UNKNOWN_1 = """
            inputs:
                - { name: training_set_columns, type: [foo-baz]}
        """
        INTERFACE_INVALID_TYPE_UNKNOWN_2 = """
            inputs:
                - { name: training_set_columns, type: 123.32}
        """


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
run_id: 6a9a5931-1c1d-47cc-aaf3-ad8b03f70575
step_id: 0c98f080-4760-46be-b35f-7dbb5e2a88c2
run_date: 1970-01-01 00:00:00.00000
data_store: I_am_a_datastore_name
storage_connection_type: AWS_BLOB
connection:
    endpoint: S3://mybucket/puppy.jpg
    access_key_id: AKIAIOSFODNN7EXAMPLE
    secret_access_key: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"""

        # https://github.com/kubeflow/pipelines/blob/e54a8e3570649bae438b649eac757d4a7e02597a/components/sample/keras/train_classifier/component.yaml
        COMPONENT_KERAS = """
schema_version: 0.1.0
schema_type: component
run_id: f4bd7cee-42f9-4f29-a21e-3f78a9bad121
step_id: c84305d1-fe42-48df-9b47-f7628172ac1d
run_date: 1970-01-01 00:00:00.00000
name: Keras - Train classifier
description: Trains classifier using Keras sequential model
inputs:
  - {name: training_set_features_path, type: {GcsPath: {data_type: TSV}}, description: 'Local or GCS path to the training set features table.'}
  - {name: training_set_labels_path, type: {GcsPath: {data_type: TSV}}, description: 'Local or GCS path to the training set labels (each label is a class index from 0 to num-classes - 1).'}
  - {name: output_model_uri, type: {GcsPath: {data_type: Keras model}}, description: 'Local or GCS path specifying where to save the trained model. The model (topology + weights + optimizer state) is saved in HDF5 format and can be loaded back by calling keras.models.load_model'} #Remove GcsUri and move to outputs once artifact passing support is checked in.
  - {name: model_config, type: {GcsPath: {data_type: Keras model config json}}, description: 'JSON string containing the serialized model structure. Can be obtained by calling model.to_json() on a Keras model.'}
  - {name: number_of_classes, type: Integer, description: 'Number of classifier classes.'}
  - {name: number_of_epochs, type: Integer, default: '100', description: 'Number of epochs to train the model. An epoch is an iteration over the entire `x` and `y` data provided.'}
  - {name: batch_size, type: Integer, default: '32', description: 'Number of samples per gradient update.'}
outputs:
  - {name: output_model_uri, type: {GcsPath: {data_type: Keras model}}, description: 'GCS path where the trained model has been saved. The model (topology + weights + optimizer state) is saved in HDF5 format and can be loaded back by calling keras.models.load_model'} #Remove GcsUri and make it a proper output once artifact passing support is checked in.
implementation:
  container:
    image: gcr.io/ml-pipeline/sample/keras/train_classifier
    command: [python3, /pipelines/component/src/train.py]
    args: [
      --training-set-features-path, {inputValue: training_set_features_path},
      --training-set-labels-path, {inputValue: training_set_labels_path},
      --output-model-path, {inputValue: output_model_uri},
      --model-config-json, {inputValue: model_config},
      --num-classes, {inputValue: number_of_classes},
      --num-epochs, {inputValue: number_of_epochs},
      --batch-size, {inputValue: batch_size},

      --output-model-path-file, {outputPath: output_model_uri},
    ]"""

        # https://github.com/kubeflow/pipelines/blob/9f6d34ff6559d607f91518259f8d4203c2f58443/components/ibm-components/commons/config/component.yaml
        COMPONENT_IBM = """
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
schema_version: 0.1.0
schema_type: component
run_id: f4bd7cee-42f9-4f29-a21e-3f78a9bad121
step_id: c84305d1-fe42-48df-9b47-f7628172ac1d
run_date: 1970-01-01 00:00:00.00000
name: 'Create Secret - Kubernetes Cluster'
description: |
  Create secret to store pipeline credentials on Kubernetes Cluster
inputs:
  - {name: token,           description: 'Required. GitHub token for accessing private repository'}
  - {name: url,             description: 'Required. GitHub raw path for accessing the credential file'}
  - {name: name,            description: 'Required. Secret Name to be stored in Kubernetes'}
outputs:
  - {name: secret_name,     description: 'Kubernetes secret name'}
implementation:
  container:
    image: docker.io/aipipeline/wml-config:latest
    command: ['python3']
    args: [
      /app/config.py,
      --token, {inputValue: token},
      --url, {inputValue: url},
      --name, {inputValue: name},
      --output-secret-name-file, {outputPath: secret_name},
    ]"""

        # https://github.com/kubeflow/pipelines/blob/9b804688d3b32e3cc8b6d89ccf4c638dc436f0ad/contrib/samples/openvino/deployer/component.yaml
        COMPONENT_OPENVINO = """
schema_version: 0.1.0
schema_type: component
run_id: f4bd7cee-42f9-4f29-a21e-3f78a9bad121
step_id: c84305d1-fe42-48df-9b47-f7628172ac1d
run_date: 1970-01-01 00:00:00.00000
name: OpenVINO model server deployer
description: Deploys OpenVINO Model Server instance to Kubernetes and runs model evaluation
inputs:
- name: Batch size
  default: auto
- name: Log level
  default: DEBUG
- name: Model export path
  default: 'gs://intelai_public_models/resnet_50_i8'
- name: Model version policy
  default: '{"latest": { "num_versions":2 }}'
- name: Replicas
  default: '1'
- name: Server name
  default: resnet
- name: Evaluation images list
  default: 'https://raw.githubusercontent.com/IntelAI/OpenVINO-model-server/master/example_client/input_images.txt'
- name: Image path prefix
  default: 'https://github.com/IntelAI/OpenVINO-model-server/raw/master/example_client/'
- name: Model input name
  default: 'data'
- name: Model output name
  default: 'prob'
- name: Model input size
  default: 224
outputs:
- name: Server endpoint
metrics:
  - name: latency
  - name: accuracy
implementation:
  container:
    image: gcr.io/constant-cubist-173123/inference_server/ml_deployer:13
    command: [./deploy.sh]
    args: [
      --model-export-path, {inputValue: Model export path},
      --server-name, {inputValue: Server name},
      --log-level, {inputValue: Log level},
      --batch-size, {inputValue: Batch size},
      --model-version-policy, {inputValue: Model version policy},
      --replicas, {inputValue: Replicas},
      --server-endpoint-output-file, {outputPath: Server endpoint},
    ]
  container:
    image: gcr.io/constant-cubist-173123/inference_server/ml_deployer:13
    command: [./evaluate.py]
    args: [
      --images_list, {inputValue: Evaluation images list},
      --image_path_prefix, {inputValue: Image path prefix},
      --grpc_endpoint, {outputValue: Server endpoint},
      --input_name, {inputValue: Model input name},
      --output_name, {inputValue: Model output name},
      --size, {inputValue: Model input size},
      --replicas, {inputValue: Replicas}
    ]"""
