""" ML Objects created by metadata passed in based on schema in mlspeclib/data """
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass, make_dataclass
from typing import NamedTuple
from collections import namedtuple

from mlspeclib.helpers import convert_yaml_to_dict, check_and_return_schema_type_by_string
from mlspeclib.schemaenums import SchemaTypes
from mlspeclib.mlschema import MLSchema
from mlspeclib.metadatavalidator import MetadataValidator

class GenericMLObject(ABC):
    """ Abstract class of an MLObject. Needs schema_enum populated to be inherited. """
    @property
    @abstractmethod
    def schema_enum(self):
        """ Abstract property to override when the specific object is instanted
        so it can return the SchemaType from schemaenums."""

@dataclass
class MLObject():
    @staticmethod
    def create_object_type(ml_schema: MLSchema, parent_name: str=None):
        """ Takes dict and builds an MLNode (sub class of namedtuple) out of it. """

        # Debating using a .map() function to do this, but I'd like to use recursion
        # and don't feel like learning how to do that
        fields = []

        for field in ml_schema.keys():
            fields.append(field)
            if isinstance(ml_schema[field], dict):
                fields.append(MLObject.create_object_type(ml_schema[field]))

        class_name = "_".join(ml_schema['schema_enum'])+"_"+ml_schema['']
        if parent_name:
            class_name += "_"+parent_name

        return make_dataclass(class_name, fields, bases=(MLObject, ))

class MLObjectsDict(dict):
    """ Portfolio of all objects instantiated as a dict. """

    # TODO: I should probably move this all to a pkl and do this load once.
    def create_and_add_object(self, verified_object_yaml):
        """Converts verified yaml to an object.
        This does not verification of the yaml against schema."""

        return # type(schema_type.name.capitalize(), (GenericMLObject,),
               # {'schema_enum': schema_type})
