import datetime
import os

import magic
import sqlalchemy as sa
from sqlalchemy import and_
from hashids import Hashids

from vobla.db.orm import Model
from vobla.db.models.users import User
from vobla.schemas import serializers
from vobla.settings import config


hashids = Hashids(salt=config["tornado"]["secret_key"], min_length=16)


class MinioMixin:
    def get_from_minio(self, minio):
        return minio.get_object(self.bucket, self.hash)


class Drop(MinioMixin, Model):
    __tablename__ = "drop"
    schema = [
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String(32)),
        sa.Column(
            "owner_id",
            sa.Integer,
            sa.ForeignKey("user.id", onupdate="CASCADE", ondelete="CASCADE"),
        ),
        sa.Column("hash", sa.String(16)),
        sa.Column("created_at", sa.DateTime, default=datetime.datetime.utcnow),
        sa.Column("is_preview_ready", sa.Boolean, default=False),
    ]
    serializer = serializers.drops.DropSchema()
    bucket = "drops"

    @classmethod
    def encode(cls, id_):
        return hashids.encode(id_, ord("d"))

    @classmethod
    def decode(cls, hash_):
        return hashids.decode(hash_)[0]

    async def serialize(self, pgc, *args, owner=None, dropfiles=None):
        if owner is None:
            owner = await User.select(pgc, User.c.id == self.owner_id)
        if dropfiles is None:
            dropfiles = await DropFile.select(
                pgc,
                and_(DropFile.c.drop_id == self.id, DropFile.c.uploaded_at.isnot(None)),
                return_list=True,
            )
        self.owner = owner
        self.dropfiles = dropfiles
        return self.serializer.dump(self, many=False).data

    @classmethod
    async def fetch(cls, pgc, filter_):
        async with pgc.begin():
            drops = await cls.select(pgc, filter_, return_list=True)
            for drop in drops:
                drop.owner = await User.select(pgc, User.c.id == drop.owner_id)
                drop.dropfiles = await DropFile.select(
                    pgc,
                    and_(
                        DropFile.c.drop_id == drop.id, DropFile.c.uploaded_at.isnot(None)
                    ),
                    return_list=True,
                )
        return drops

    @classmethod
    async def create(cls, pgc, owner, name=None):
        async with pgc.begin():
            obj = cls(name=name and name[:32], owner_id=owner.id)
            await obj.insert(pgc, [obj.c.created_at])
            obj.hash = "{}".format(obj.encode(obj.id))
            if name is None:
                obj.name = obj.hash
            await obj.update(pgc)
            return obj


class DropFile(MinioMixin, Model):
    __tablename__ = "drop_file"
    schema = [
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String(32)),
        sa.Column(
            "drop_id",
            sa.Integer,
            sa.ForeignKey("drop.id", onupdate="CASCADE", ondelete="CASCADE"),
        ),
        sa.Column("hash", sa.String(16)),
        sa.Column("mimetype", sa.String(32)),
        sa.Column("created_at", sa.DateTime, default=datetime.datetime.utcnow),
        sa.Column("uploaded_at", sa.DateTime, nullable=True),
    ]
    serializer = serializers.drops.DropFileSchema()
    bucket = "dropfiles"

    @classmethod
    def encode(cls, id_):
        return hashids.encode(id_, ord("f"))

    @classmethod
    def decode(cls, hash_):
        return hashids.decode(hash_)[0]

    @classmethod
    async def create(cls, pgc, drop, name=None):
        async with pgc.begin():
            obj = cls(name=name and name[:32], drop_id=drop.id)
            await obj.insert(pgc, [obj.c.created_at])
            obj.hash = "{}".format(obj.encode(obj.id))
            await obj.update(pgc)
            return obj

    def set_mimetype(self, buffer, filename: str = None):
        mimetype = magic.from_buffer(buffer, mime=True)
        if mimetype.startswith("text") and filename:
            languages = dict(
                py="python",
                js="javascript",
                jsx="jsx",
                css="css",
                html="html",
                php="php",
                rb="ruby",
                sh="bash",
                sql="sql",
                swift="swift",
                yml="yaml",
                yaml="yaml",
                c="c",
                cpp="cpp",
                hpp="cpp",
                java="java",
                md="markdown",
                cs="csharp",
                rs="rust",
                go="go",
                hs="haskell",
                coffee="coffescript",
                sass="sass",
                scss="scss",
                less="less",
                ts="typescript",
                erl="erlang",
                lua="lua",
                pl="perl",
                pug="pug",
                groovy="groovy",
                scala="scala",
            )
            lang = languages.get(os.path.splitext(filename)[1][1:], None)
            if lang:
                mimetype = f"text/x-{lang}"
        self.mimetype = mimetype
