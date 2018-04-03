import random

import psycopg2
import jwt
import sqlalchemy as sa
from passlib.hash import pbkdf2_sha256

from vobla.settings import config
from vobla.db.orm import Model


JWT_ALGORITHM = 'HS256'


class User(Model):
    __tablename__ = 'user'
    schema = [
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('email', sa.String(60), nullable=False, unique=True),
        sa.Column('password_hash', sa.String(87), nullable=False)
    ]
    _hash_fn = pbkdf2_sha256

    def verify_password(self, password):
        return self._hash_fn.verify(
            password, self.password_hash
        )

    def hash_password(self, password):
        self.password_hash = self._hash_fn.hash(password)

    @classmethod
    async def verify_jwt(cls, pgc, token):
        try:
            data = jwt.decode(
                token,
                config['tornado']['secret_key'],
                algorithms=[JWT_ALGORITHM]
            )
            if 'email' in data:
                obj = await cls.select(pgc, cls.c.email == data['email'])
                if obj:
                    return obj
        except jwt.exceptions.DecodeError:
            pass
        return None

    def make_jwt(self):
        return (
            jwt.encode(
                dict(email=self.email),
                config['tornado']['secret_key'],
                algorithm=JWT_ALGORITHM
            ).decode('ascii')
        )


class UserInvite(Model):
    __tablename__ = 'user_invite'
    schema = [
        sa.Column('code', sa.String(8), nullable=False, primary_key=True)
    ]

    @staticmethod
    async def create(pgc):
        r = random.SystemRandom()
        while True:
            code = ''.join(r.choice('0123456789ABCDEF') for i in range(6))
            try:
                ui = await UserInvite.insert(pgc, dict(code=code))
            except psycopg2.IntegrityError:
                continue
            return ui
