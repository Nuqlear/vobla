from vobla.schemas import BaseSchema

from marshmallow import fields


class SuccessfulAuthSchema(BaseSchema):
    token = fields.Str(required=True)
