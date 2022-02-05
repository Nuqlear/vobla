import random

import psycopg2
import sqlalchemy as sa

from vobla.db.orm import Model





class User(Model):
    __tablename__ = "user"
    schema = [
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("email", sa.String(60), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(87), nullable=False),
        sa.Column("active_session_hash", sa.String(87), nullable=False),
    ]


class UserInvite(Model):
    __tablename__ = "user_invite"
    schema = [sa.Column("code", sa.String(8), nullable=False, primary_key=True)]

    @staticmethod
    async def create(pgc):
        r = random.SystemRandom()
        while True:
            code = "".join(r.choice("0123456789ABCDEF") for i in range(6))
            try:
                ui = await UserInvite.insert(pgc, dict(code=code))
            except psycopg2.IntegrityError:
                continue
            return ui
