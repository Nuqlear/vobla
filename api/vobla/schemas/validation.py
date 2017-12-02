from vobla.schemas import BaseSchema

from marshmallow import fields


class ValidationErrorSchema(BaseSchema):

    class InnerValidationErrorSchema(BaseSchema):

        class ValidationFieldErrorSchema(BaseSchema):
            field = fields.Str()

        message = fields.Str()
        validation = fields.Nested(ValidationFieldErrorSchema)

    error = fields.Nested(InnerValidationErrorSchema)
