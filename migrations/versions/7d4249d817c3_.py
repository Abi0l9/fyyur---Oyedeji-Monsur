"""empty message

Revision ID: 7d4249d817c3
Revises: 238efa759fb6
Create Date: 2022-08-02 22:22:21.344402

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7d4249d817c3'
down_revision = '238efa759fb6'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('artist', sa.Column('looking_for_talent', sa.Boolean(), nullable=True))
    op.add_column('artist', sa.Column('seeking_description', sa.String(length=500), nullable=True))
    op.drop_column('artist', 'details')
    op.drop_column('artist', 'songs')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('artist', sa.Column('songs', sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('artist', sa.Column('details', sa.TEXT(), autoincrement=False, nullable=True))
    op.drop_column('artist', 'seeking_description')
    op.drop_column('artist', 'looking_for_talent')
    # ### end Alembic commands ###
