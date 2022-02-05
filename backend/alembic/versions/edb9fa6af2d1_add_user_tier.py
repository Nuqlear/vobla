"""add_user_tier

Revision ID: edb9fa6af2d1
Revises: d0dae9386eb2
Create Date: 2022-02-05 17:54:03.253193

"""
import os

import datetime
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "edb9fa6af2d1"
down_revision = "d0dae9386eb2"
branch_labels = None
depends_on = None


user = sa.table(
    "user",
    sa.column("id", sa.Integer()),
    sa.column("user_tier_id", sa.String),
)
user_tier = sa.table(
    "user_tier",
    sa.column("id", sa.String()),
    sa.column("name", sa.String()),
    sa.column("max_drop_file_size", sa.Integer()),
    sa.column("max_storage_size", sa.Integer()),
    sa.column("created_at", sa.DateTime()),
    sa.column("updated_at", sa.DateTime()),
)


def upgrade():
    op.create_table(
        "user_tier",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("name", sa.String(length=60), nullable=False),
        sa.Column("max_drop_file_size", sa.Integer(), nullable=True),
        sa.Column("max_storage_size", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.add_column("user", sa.Column("user_tier_id", sa.String(), nullable=True))
    op.add_column("drop_file", sa.Column("size", sa.Integer(), nullable=False))
    op.create_foreign_key(None, "user", "user_tier", ["user_tier_id"], ["id"])
    if os.environ["ENV"] != "tests":
        conn = op.get_bind()
        _insert_user_tiers(conn)
        _set_user_tiers(conn)
    op.alter_column(
        "user",
        "user_tier_id",
        existing_type=sa.String,
        nullable=False,
    )


def _set_user_tiers(conn):
    user_tier_id = conn.execute(
        sa.select([user_tier.c.id]).where(user_tier.c.name == "Basic")
    ).scalar()
    conn.execute(user.update().values({user.c.user_tier_id: user_tier_id}))


def _insert_user_tiers(conn):
    utcnow = datetime.datetime.utcnow()
    conn.execute(
        user_tier.insert().values(
            [
                {
                    "id": "basic",
                    "name": "Basic",
                    "max_drop_file_size": 31457280,
                    "max_storage_size": 314572800,
                    "created_at": utcnow,
                    "updated_at": utcnow,
                },
                {
                    "id": "super",
                    "name": "Super",
                    "max_drop_file_size": None,
                    "max_storage_size": None,
                    "created_at": utcnow,
                    "updated_at": utcnow,
                }
            ]
        )
    )


def downgrade():
    op.drop_constraint(None, 'user', type_='foreignkey')
    op.drop_column("user", "user_tier_id")
    op.drop_table("user_tier")
