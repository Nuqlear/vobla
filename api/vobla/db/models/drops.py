import datetime
import os

import sqlalchemy as sa
from hashids import Hashids

from vobla.db.orm import Model
from vobla.db.models.users import User
from vobla.settings import config


hashids = Hashids(salt=config['tornado']['secret_key'], min_length=16)


class GenHashMixin(object):

    @staticmethod
    def gen_hash(*args):
        return hashids.encode(*args)


class Drop(Model, GenHashMixin):
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

    @classmethod
    async def fetch_and_serialize(cls, pgc, id_or_ids):
        async with pgc.begin():
            if isinstance(id_or_ids, list):
                drop = await cls.select(cls.c.id==id_or_ids)
                owner = await User.select(id==drop.owner_id)
                files = await DropFile.select(
                    cls.c.drop_id==id_or_ids, cls.c.uploaded_at!=None,
                    return_list=True
                )
                return {
                    'name': drop.name,
                    'hash': drop.hash,
                    'created_at': drop.created_at,
                    'owner': {
                        'email': owner.email
                    },
                    'dropfiles': [
                        {
                            'name': file.name,
                            'hash': file.hash,
                            'mimetype': file.mimetype,
                            'uploaded_at': file.uploaded_at
                        }
                        for file in files
                    ]
                }
            else:
                query = (
                    cls.t.select().where(Drop.c.id.in_(id_or_ids))
                    .order_by(Drop.c.id)
                )
                cursor = await pgc.execute(query)
                res = await cursor.fetchmany()
                return res

    @classmethod
    async def create(cls, pgc, owner, name=None):
        async with pgc.begin():
            obj = cls(name=name, owner_id=owner.id)
            await obj.insert(pgc, [obj.c.created_at])
            obj.hash = '{}'.format(cls.gen_hash(obj.id, ord('d')))
            if name is None:
                obj.name = obj.hash
            await obj.update(pgc)
            return obj


class DropFile(Model, GenHashMixin):
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
                os.path.dirname(obj.file_path), obj.tmp_folder_path
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
    def tmp_folder_path(self):
        year = self.created_at.strftime('%y')
        month = self.created_at.strftime('%m')
        day = self.created_at.strftime('%d')
        return os.path.join(
            config['vobla']['temp_upload_folder'],
            year, month, day, self.hash
        )
