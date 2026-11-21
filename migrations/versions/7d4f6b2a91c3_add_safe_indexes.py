"""Add safe lookup indexes for MGMS production tables.

Revision ID: 7d4f6b2a91c3
Revises: f108c1017e0b
Create Date: 2026-11-21
"""

from alembic import op

revision = "7d4f6b2a91c3"
down_revision = "f108c1017e0b"
branch_labels = None
depends_on = None


def upgrade():
    op.create_index("ix_users_role", "users", ["role"], unique=False)
    op.create_index("ix_documents_category", "documents", ["category"], unique=False)
    op.create_index("ix_documents_created_at", "documents", ["created_at"], unique=False)


def downgrade():
    op.drop_index("ix_documents_created_at", table_name="documents")
    op.drop_index("ix_documents_category", table_name="documents")
    op.drop_index("ix_users_role", table_name="users")
