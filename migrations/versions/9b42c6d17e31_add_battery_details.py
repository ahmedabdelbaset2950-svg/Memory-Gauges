"""Add battery details

Revision ID: 9b42c6d17e31
Revises: 04bee121dc03
Create Date: 2026-07-27
"""
from alembic import op
import sqlalchemy as sa

revision = '9b42c6d17e31'
down_revision = '04bee121dc03'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('batteries', schema=None) as batch_op:
        batch_op.add_column(sa.Column('compatible_gauge_type', sa.String(length=120), nullable=True))
        batch_op.add_column(sa.Column('capacity', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('capacity_unit', sa.String(length=10), nullable=True))
        batch_op.add_column(sa.Column('status', sa.String(length=50), nullable=True))
        batch_op.add_column(sa.Column('notes', sa.Text(), nullable=True))

    op.execute("UPDATE batteries SET compatible_gauge_type = 'Unknown' WHERE compatible_gauge_type IS NULL")
    op.execute("UPDATE batteries SET capacity = 0 WHERE capacity IS NULL")
    op.execute("UPDATE batteries SET capacity_unit = 'Ah' WHERE capacity_unit IS NULL")
    op.execute("UPDATE batteries SET status = 'Available' WHERE status IS NULL")

    with op.batch_alter_table('batteries', schema=None) as batch_op:
        batch_op.alter_column('compatible_gauge_type', existing_type=sa.String(length=120), nullable=False)
        batch_op.alter_column('capacity', existing_type=sa.Float(), nullable=False)
        batch_op.alter_column('capacity_unit', existing_type=sa.String(length=10), nullable=False)
        batch_op.alter_column('status', existing_type=sa.String(length=50), nullable=False)


def downgrade():
    with op.batch_alter_table('batteries', schema=None) as batch_op:
        batch_op.drop_column('notes')
        batch_op.drop_column('status')
        batch_op.drop_column('capacity_unit')
        batch_op.drop_column('capacity')
        batch_op.drop_column('compatible_gauge_type')
