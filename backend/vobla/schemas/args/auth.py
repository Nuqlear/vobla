from vobla.schemas import BaseSchema

from marshmallow import fields


class UserLoginSchema(BaseSchema):
    email = fields.Str(required=True)
    password = fields.Str(required=True)


class UserSignupSchema(BaseSchema):
    email = fields.Str(required=True)
    password = fields.Str(required=True)
    invite_code = fields.Str(required=True)
