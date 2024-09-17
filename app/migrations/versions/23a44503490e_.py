"""empty message

Revision ID: 23a44503490e
Revises: fe9f4c58c2cc
Create Date: 2024-09-17 13:56:30.209322

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '23a44503490e'
down_revision = 'fe9f4c58c2cc'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('coding_task_submission',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('code', sa.String(length=3000), nullable=False),
    sa.Column('code_result', sa.String(length=3000), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('task_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('passed', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['task_id'], ['coding_task.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('coding_task_submission')
    # ### end Alembic commands ###
