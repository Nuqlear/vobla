import datetime
import enum

import sqlalchemy as sa
from sqlalchemy_utils import ChoiceType

from vobla.db.orm import Model
from vobla.settings import config


class UserTierEnum(enum.Enum):
    basic = 'basic'
    super_ = 'super'

    @classmethod
    def default(cls):
        return getattr(cls, config["vobla"]["default_user_tier"])


class UserTier(Model):
    __tablename__ = "user_tier"
    schema = [
        sa.Column("id", ChoiceType(UserTierEnum), primary_key=True),
        sa.Column("name", sa.String(60), nullable=False, unique=True),
        sa.Column("max_drop_file_size", sa.Integer, nullable=True),
        sa.Column("max_storage_size", sa.Integer, nullable=True),
        sa.Column("created_at", sa.DateTime, default=datetime.datetime.utcnow),
        sa.Column("updated_at", sa.DateTime, default=datetime.datetime.utcnow),
    ]


class User(Model):
    __tablename__ = "user"
    schema = [
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("email", sa.String(60), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(87), nullable=False),
        sa.Column("active_session_hash", sa.String(87), nullable=False),
        sa.Column(
            "user_tier_id",
            ChoiceType(UserTierEnum),
            sa.ForeignKey("user_tier.id", onupdate="CASCADE", ondelete="CASCADE"),
            nullable=False,
        ),
    ]
