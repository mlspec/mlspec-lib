from tokenize import String
from pathlib import Path

from mlspeclib.mlschema import MLSchema

import tempfile

import uuid


import git
from git import GitCommandError

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
