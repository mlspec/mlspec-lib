import sys
from tokenize import String
import yaml
from pathlib import Path

from mlspeclib.mlschema import MLSchema
from mlspeclib.mlschemaenums import MLSchemaTypes
from mlspeclib.mlobject import MLObject

import tempfile

import json
import uuid

import traceback

import logging
import base64
import git
from git import GitCommandError
import tempfile

class GitHubSchemas:
    @staticmethod
    def add_schemas_from_github_url(git_url: String):
        with tempfile.TemporaryDirectory() as td:
            try:
                git.Git(td).clone(
                    git_url, str(uuid.uuid4()), depth=1
                )
            except GitCommandError as gce:
                raise Exception(
                    f"Trying to read from the git repo ({git_url}) and write to the directory ({td}). Full error follows: {str(gce)}"
                )

            MLSchema.append_schema_to_registry(Path(td))
