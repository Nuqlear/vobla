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
