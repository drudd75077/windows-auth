"""add new columns to user table

Revision ID: 78588193f474
Revises: ad59210acf2a
Create Date: 2025-04-01 00:15:35.141038

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '78588193f474'
down_revision = 'ad59210acf2a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False))
        batch_op.add_column(sa.Column('last_login', sa.DateTime(timezone=True), nullable=True))
        batch_op.add_column(sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False))
        batch_op.add_column(sa.Column('created_by', sa.String(length=80), nullable=True))
        batch_op.add_column(sa.Column('updated_by', sa.String(length=80), nullable=True))
        batch_op.add_column(sa.Column('is_active', sa.Boolean(), server_default=sa.text('1'), nullable=False))
        batch_op.drop_index('ix_user_username')
        batch_op.create_unique_constraint('uq_user_username', ['username'])

def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_constraint('uq_user_username', type_='unique')
        batch_op.create_index('ix_user_username', ['username'], unique=1)
        batch_op.drop_column('is_active')
        batch_op.drop_column('updated_by')
        batch_op.drop_column('created_by')
        batch_op.drop_column('updated_at')
        batch_op.drop_column('last_login')
        batch_op.drop_column('created_at')

    # ### end Alembic commands ###