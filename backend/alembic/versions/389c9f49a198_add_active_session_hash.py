"""add_active_session_hash

Revision ID: 389c9f49a198
Revises: ade758194506
Create Date: 2022-02-05 15:16:47.122088

"""
import random

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "389c9f49a198"
down_revision = "ade758194506"
branch_labels = None
depends_on = None


user = sa.table(
    "user",
    sa.column("id", sa.Integer()),
    sa.column("active_session_hash", sa.String(87)),
)


def upgrade():
    op.add_column(
        "user", sa.Column("active_session_hash", sa.String(87), nullable=True)
    )
    _set_session_hash()
    op.alter_column(
        "user",
        "active_session_hash",
        existing_type=sa.String(length=87),
        nullable=False,
    )


def _set_session_hash():
    conn = op.get_bind()
    rows = conn.execute(user.select()).fetchall()
    for row in rows:
        r = random.SystemRandom()
        active_session_hash = "".join(r.choice("0123456789ABCDEF") for i in range(87))
        conn.execute(
            user.update()
            .values(
                {
                    user.c.active_session_hash: active_session_hash,
                }
            )
            .where(user.c.id == row.id)
        )


def downgrade():
    op.drop_column("user", "active_session_hash")
