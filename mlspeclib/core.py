# -*- coding: utf-8 -*-
from . import helpers

import os, sys
from pathlib import Path
import semver
import strictyaml
from mlspeclib.metadatavalidator import MetadataValidator
import cerberus

class PopulateRegistry(object):
    def __init__(self):
        pass

if __name__ == '__main__':
    pr = PopulateRegistry()
