from marshmallow import Schema


class BaseSchema(Schema):

    class Meta:
        strict = True


from vobla.schemas import args
from vobla.schemas import serializers
