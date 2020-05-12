""" Functions for loading and saving files to disk. """
from pathlib import Path

from mlspeclib.mlschema import MLSchema
from mlspeclib.helpers import convert_dict_to_yaml


class IO:
    """ Core IO class for reading and writing files."""
    @staticmethod
    def get_content_from_path(filepath: str) -> str:
        """ Takes a string, converts to a pathlib Path and loads the file as text. """
        return IO._load(filepath)

    @staticmethod
    def write_content_to_path(filepath: str, content):
        """ Takes a string, converts to a pathlib Path and writes the file as text. """
        if isinstance(content, dict):
            content_as_string = convert_dict_to_yaml(content)
        else:
            content_as_string = content
        return IO._save(filepath, content_as_string)

    # Moved to a function to allow swapping out for other libraries
    @staticmethod
    def _load(filepath: str) -> str:
        """ Internal load function, uses Path.read_text(encoding="utf-8")."""
        return Path(filepath).read_text(encoding="utf-8")

    # Moved to a function to allow swapping out for other libraries
    @staticmethod
    def _save(filepath: str, content: str):
        """ Writes file to disk using Path.write_text()."""
        return Path(filepath).write_text(content)
