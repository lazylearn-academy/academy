"""empty message

Revision ID: e6141a113d2e
Revises: 82f914194752
Create Date: 2024-09-18 06:59:20.045452

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e6141a113d2e'
down_revision = '82f914194752'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user_theme',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('theme_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['theme_id'], ['theme.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('user_id', 'theme_id'),
    info={'bind_key': None}
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user_theme')
    # ### end Alembic commands ###
