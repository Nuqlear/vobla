from vobla.schemas import BaseSchema

from marshmallow import fields


def build_dropfile_url(hash):
    return f'/f/{hash}'


def build_drop_url(hash):
    return f'/d/{hash}'


class DropFileFirstChunkUploadSchema(BaseSchema):
    drop_file_hash = fields.Str(required=True)
    drop_hash = fields.Str(required=True)
    url = fields.Method('_get_url')

    def _get_url(self, obj):
        return build_dropfile_url(obj['drop_file_hash'])


class DropSchema(BaseSchema):

    class OwnerSchema(BaseSchema):
        email = fields.Str(required=True)

    class DropFileSchema(BaseSchema):
        name = fields.Str(required=True)
        hash = fields.Str(required=True)
        mimetype = fields.Str(required=True)
        uploaded_at = fields.DateTime(required=True)
        url = fields.Method('_get_url')

        def _get_url(self, obj):
            return build_dropfile_url(obj.hash)

    name = fields.Str(required=True)
    hash = fields.Str(required=True)
    created_at = fields.DateTime(required=True)
    owner = fields.Nested(OwnerSchema, required=True)
    dropfiles = fields.Nested(DropFileSchema, many=True)
    url = fields.Method('_get_url')

    def _get_url(self, obj):
        return build_drop_url(obj.hash)


class UserDropsSchema(BaseSchema):
    drops = fields.Nested(DropSchema, many=True)
    next_cursor = fields.Str(required=False)
