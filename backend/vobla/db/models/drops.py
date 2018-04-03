import datetime
import os
from collections import Iterable

import sqlalchemy as sa
from sqlalchemy import and_
from hashids import Hashids

from vobla.db.orm import Model
from vobla.db.models.users import User
from vobla.schemas import serializers
from vobla.settings import config


hashids = Hashids(salt=config['tornado']['secret_key'], min_length=16)


class Drop(Model):
    __tablename__ = 'drop'
    schema = [
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String(32)),
        sa.Column(
            'owner_id',
            sa.Integer,
            sa.ForeignKey('user.id', onupdate="CASCADE", ondelete="CASCADE")
        ),
        sa.Column('hash', sa.String(16)),
        sa.Column('created_at', sa.DateTime, default=datetime.datetime.utcnow)
    ]
    serializer = serializers.drops.DropSchema()

    async def serialize(self, pgc, *args, owner=None, dropfiles=None):
        if owner is None:
            owner = await User.select(pgc, User.c.id == self.owner_id)
        if dropfiles is None:
            dropfiles = await DropFile.select(
                pgc,
                and_(
                    DropFile.c.drop_id == self.id,
                    DropFile.c.uploaded_at.isnot(None),
                ),
                return_list=True
            )
        self.owner = owner
        self.dropfiles = dropfiles
        return self.serializer.dump(self, many=False).data

    @classmethod
    async def fetch(cls, pgc, ids):
        async with pgc.begin():
            if not isinstance(ids, Iterable):
                ids = [ids]
            drops = await cls.select(
                pgc, cls.c.id.in_(ids), return_list=True
            )
            for drop in drops:
                drop.owner = await User.select(pgc, User.c.id == drop.owner_id)
                drop.dropfiles = await DropFile.select(
                    pgc,
                    and_(
                        DropFile.c.drop_id == drop.id,
                        DropFile.c.uploaded_at.isnot(None),
                    ),
                    return_list=True
                )
        return drops

    @classmethod
    async def create(cls, pgc, owner, name=None):
        async with pgc.begin():
            obj = cls(name=name, owner_id=owner.id)
            await obj.insert(pgc, [obj.c.created_at])
            obj.hash = '{}'.format(hashids.encode(obj.id, ord('d')))
            if name is None:
                obj.name = obj.hash
            await obj.update(pgc)
            return obj


class DropFile(Model):
    __tablename__ = 'drop_file'
    schema = [
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String(32)),
        sa.Column(
            'drop_id',
            sa.Integer,
            sa.ForeignKey('drop.id', onupdate="CASCADE", ondelete="CASCADE")
        ),
        sa.Column('hash', sa.String(16)),
        sa.Column('mimetype', sa.String(32)),
        sa.Column('created_at', sa.DateTime, default=datetime.datetime.utcnow),
        sa.Column('uploaded_at', sa.DateTime, nullable=True)
    ]

    @classmethod
    async def create(cls, pgc, drop, name=None):
        async with pgc.begin():
            obj = cls(name=name, drop_id=drop.id)
            await obj.insert(pgc, [obj.c.created_at])
            obj.hash = '{}'.format(hashids.encode(obj.id, ord('f')))
            await obj.update(pgc)
            for folder in (
                os.path.dirname(obj.file_path), obj.temp_folder_path
            ):
                os.makedirs(folder, exist_ok=True)
            return obj

    @property
    def file_path(self):
        year = self.created_at.strftime('%y')
        month = self.created_at.strftime('%m')
        day = self.created_at.strftime('%d')
        return os.path.join(
            config['vobla']['upload_folder'],
            year, month, day, self.hash
        )

    @property
    def temp_folder_path(self):
        year = self.created_at.strftime('%y')
        month = self.created_at.strftime('%m')
        day = self.created_at.strftime('%d')
        return os.path.join(
            config['vobla']['temp_upload_folder'],
            year, month, day, self.hash
        )
