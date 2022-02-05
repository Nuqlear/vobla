from vobla.schemas import BaseSchema

from marshmallow import fields


class VoblaHTTPErrorSchema(BaseSchema):
    class InnerValidationErrorSchema(BaseSchema):
        message = fields.Str(required=True)

    error = fields.Nested(InnerValidationErrorSchema, required=True)


class ValidationErrorSchema(BaseSchema):
    class InnerValidationErrorSchema(BaseSchema):
        class ValidationFieldErrorSchema(BaseSchema):
            field = fields.Str(required=True)

        message = fields.Str(required=True, default="Validation error")
        fields = fields.Nested(ValidationFieldErrorSchema, required=True)

    error = fields.Nested(InnerValidationErrorSchema, required=True)
