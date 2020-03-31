import sys
import collections

class MLObjects(dict):
# Trying to figure out a better way to do this rather than reading in everything from disk every time
# this is instantiated. Oh well.
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    

