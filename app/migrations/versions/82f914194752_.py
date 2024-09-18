"""empty message

Revision ID: 82f914194752
Revises: 23a44503490e
Create Date: 2024-09-17 20:51:24.128350

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '82f914194752'
down_revision = '23a44503490e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user_theme')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user_theme',
    sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('theme_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['theme_id'], ['theme.id'], name='user_theme_theme_id_fkey'),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], name='user_theme_user_id_fkey'),
    sa.PrimaryKeyConstraint('user_id', 'theme_id', name='user_theme_pkey')
    )
    # ### end Alembic commands ###