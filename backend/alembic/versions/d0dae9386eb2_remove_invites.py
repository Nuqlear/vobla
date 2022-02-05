"""remove_invites

Revision ID: d0dae9386eb2
Revises: 389c9f49a198
Create Date: 2022-02-05 15:57:13.804401

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "d0dae9386eb2"
down_revision = "389c9f49a198"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_table("user_invite")


def downgrade():
    op.create_table(
        "user_invite",
        sa.Column("code", sa.String(length=8), nullable=False),
        sa.PrimaryKeyConstraint("code"),
    )
