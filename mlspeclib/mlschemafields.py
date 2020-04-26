""" Extension fields for MLSchema, specifically for datetime \
which doesn't work right now from yaml """
from datetime import datetime

from marshmallow import fields

from uuid import UUID


# pylint: disable=missing-class-docstring, too-few-public-methods
class MLSchemaFields:

    ALL_FIELD_TYPES = {
        "Raw": "raw",
        "Nested": "nested",
        "Dict": dict,
        "List": list,
        "Tuple": tuple,
        "String": str,
        "UUID": UUID,
        "Integer": int,
        "Boolean": bool,
        "Float": float,
        "DateTime": datetime,
        "Url": "url",
        "URL": "uri",
        "Email": "email",
        "Str": str,
        "Bool": bool,
        "Int": int,
    }

    class MLField(fields.Field):
        """ Subclassing of Marshmallow field for everything we want to extend in MLSchema """

        identity_type: type

        def _deserialize(self, value, attr, data, **kwargs):
            if isinstance(value, self.identity_type):
                return value
            return super()._deserialize(value, attr, data, **kwargs)

    class DateTime(MLField, fields.DateTime):
        identity_type = datetime
