""" Functions for loading and saving files to disk. """
from pathlib import Path

from mlspeclib.mlschema import MLSchema

class IO:
    """ Core IO class for reading and writing files."""
    @staticmethod
    def get_object_from_path(file: str):
        all_text = IO.load(file)
        created_object = MLSchema.create_object(all_text)

    @staticmethod
    def load(file: str):
        return Path(file).read_text()
