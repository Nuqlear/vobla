from vobla.schemas import BaseSchema

from marshmallow import fields


class DropFileUploadedSchema(BaseSchema):
    drop_file_hash = fields.Str(required=True)
    drop_hash = fields.Str(required=True)
