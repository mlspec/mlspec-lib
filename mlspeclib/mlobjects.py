""" ML Objects created by metadata passed in based on schema in mlspeclib/data """
from abc import ABC, abstractmethod

class GenericMLObject(ABC):
    """ Abstract class of an MLObject. Needs schema_enum populated to be inherited. """
    @property
    @abstractmethod
    def schema_enum(self):
        """ Abstract property to override when the specific object is instanted
        so it can return the SchemaType from schemaenums."""

class MLObjects(dict):
    """ Portfolio of all objects instantiated as a dict. """
    # Trying to figure out a better way to do this rather
    # than reading in everything from disk every time
    # this is instantiated. Oh well.
    def load_object(self, verified_object_yaml):
        """Converts verified yaml to an object. Does NOT add it to the dict.
        This does not verification of the yaml against schema."""
