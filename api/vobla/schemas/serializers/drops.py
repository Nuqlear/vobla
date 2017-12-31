from vobla.schemas import BaseSchema

from marshmallow import fields


class DropFileFirstChunkUploadSchema(BaseSchema):
    drop_file_hash = fields.Str(required=True)
    drop_hash = fields.Str(required=True)


class DropSchema(BaseSchema):

    class OwnerSchema(BaseSchema):
        email = fields.Str(required=True)

    class DropFileSchema(BaseSchema):
        name = fields.Str(required=True)
        hash = fields.Str(required=True)
        mimetype = fields.Str(required=True)
        uploaded_at = fields.DateTime(required=True)

    name = fields.Str(required=True)
    hash = fields.Str(required=True)
    created_at = fields.DateTime(required=True)
    owner = fields.Nested(OwnerSchema, required=True)
    dropfiles = fields.Nested(DropFileSchema, many=True)
