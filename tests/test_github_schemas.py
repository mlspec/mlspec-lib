# pylint: disable=protected-access,missing-function-docstring, missing-class-docstring, missing-module-docstring, missing-class-docstring # noqa
# -*- coding: utf-8 -*-
import unittest
import tempfile
from io import StringIO
from pathlib import Path
from unittest.mock import patch

from marshmallow import ValidationError, pprint
import marshmallow.class_registry

from mlspeclib.mlschema import MLSchema
from mlspeclib.experimental.github import GitHubSchemas

import logging

class githubSchemasTests(unittest.TestCase):  # pylint: disable=invalid-name
    """github test cases."""

    default_registry = None

    def setUp(self):
        if githubSchemasTests.default_registry is None:
            githubSchemasTests.default_registry = marshmallow.class_registry._registry.copy()
        else:
            marshmallow.class_registry._registry = githubSchemasTests.default_registry.copy()

        self.test_dir = tempfile.TemporaryDirectory()

    def tearDown(self):
        # Close the file, the directory will be removed after the test
        self.test_dir.cleanup()

    def test_add_schemas_from_url(self):

        MLSchema.populate_registry()
        load_url = "https://github.com/mlspec/mlspeclib-action-samples-schemas"

        current_schema_total = len(marshmallow.class_registry._registry)

        mock_stdout = StringIO()
        rootLogger = logging.getLogger()
        rootLogger.addHandler(logging.StreamHandler(mock_stdout))

        GitHubSchemas.add_schemas_from_github_url(load_url)

        self.assertTrue(
            (current_schema_total + 58)
            == len(marshmallow.class_registry._registry)
        )


if __name__ == "__main__":
    unittest.main()
