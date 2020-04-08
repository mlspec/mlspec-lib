""" Functions for loading and saving files to disk. """
from pathlib import Path

from mlspeclib.mlschema import MLSchema

class IO:
    """ Core IO class for reading and writing files."""
    @staticmethod
    def get_object_from_path(file: str):
        """ Takes a string, converts to a pathlib Path and loads the file as text. """
        return MLSchema.create_object(IO._load(file))

    @staticmethod
    def _load(file: str):
        """ Internal load function, moved to a function to allow for swapping \
            out for other libs if necessary."""
        return Path(file).read_text()
