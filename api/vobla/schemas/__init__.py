from marshmallow import Schema


class BaseSchema(Schema):

    class Meta:
        strict = True


from . import auth
from . import validation
from . import drops
