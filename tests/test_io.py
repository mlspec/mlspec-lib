# pylint: disable=protected-access,missing-function-docstring, missing-class-docstring
# pylint: disable=missing-module-docstring, missing-class-docstring
# -*- coding: utf-8 -*-
import unittest
from pathlib import Path
import mock

from mlspeclib.mlschema import MLSchema
from mlspeclib.io import IO


class test_io(unittest.TestCase):  # pylint: disable=invalid-name
    """io test cases."""

    def test_load_file_from_disk(self):
        all_objects = []

        MLSchema.populate_registry()

        all_objects.append(
            IO.get_content_from_path(Path("tests/data/0/0/1/datapath.yaml"))
        )

        self.assertTrue(len(all_objects) == 1)

    @mock.patch("pathlib.PosixPath.write_text")
    def test_save_file(self, mock_write_text):
        mock_write_text.return_value = True

        self.assertTrue(IO.write_content_to_path("A_PATH", "A_STRING"))


if __name__ == "__main__":
    unittest.main()
