"""Add reports maintenance and information samples

Revision ID: c84f3b9e1a20
Revises: 9b42c6d17e31
"""
from alembic import op
import sqlalchemy as sa

revision = 'c84f3b9e1a20'
down_revision = '9b42c6d17e31'
branch_labels = None
depends_on = None

def upgrade():
    with op.batch_alter_table('information_rows') as batch_op:
        batch_op.add_column(sa.Column('total_samples', sa.Integer(), nullable=True, server_default='0'))
    op.create_table('maintenance_records',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('equipment_type', sa.String(length=30), nullable=False),
        sa.Column('serial_number', sa.String(length=120), nullable=False),
        sa.Column('maintenance_date', sa.Date(), nullable=False),
        sa.Column('problem', sa.Text(), nullable=False),
        sa.Column('action_taken', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=30), nullable=False),
        sa.Column('return_date', sa.Date(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_maintenance_records_serial_number'), 'maintenance_records', ['serial_number'], unique=False)

def downgrade():
    op.drop_index(op.f('ix_maintenance_records_serial_number'), table_name='maintenance_records')
    op.drop_table('maintenance_records')
    with op.batch_alter_table('information_rows') as batch_op:
        batch_op.drop_column('total_samples')
