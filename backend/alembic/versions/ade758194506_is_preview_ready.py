"""is_preview_ready

Revision ID: ade758194506
Revises: fbb90f77d108
Create Date: 2018-06-02 01:56:17.005979

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ade758194506'
down_revision = 'fbb90f77d108'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('drop', sa.Column('is_preview_ready', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('drop', 'is_preview_ready')
    op.drop_table('model')
    # ### end Alembic commands ###
