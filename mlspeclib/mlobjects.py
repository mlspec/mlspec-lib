import sys
import collections

from abc import ABC, abstractmethod

from mlspeclib.schemaenums import SchemaTypes

#pylint: disable=abstract-class-instantiated
class GenericMLObject(ABC):
    @property
    @abstractmethod
    def schema_enum(self): 
        pass 

class MLObjects(dict):
# Trying to figure out a better way to do this rather than reading in everything from disk every time
# this is instantiated. Oh well.
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def load_object(self, verified_object_yaml):
        pass