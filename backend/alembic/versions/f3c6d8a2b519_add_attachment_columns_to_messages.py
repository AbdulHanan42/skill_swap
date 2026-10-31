"""Add attachment columns to messages for chat file sharing

Revision ID: f3c6d8a2b519
Revises: e7a4c1b9d3f2
Create Date: 2026-10-31 17:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f3c6d8a2b519'
down_revision: Union[str, Sequence[str], None] = 'e7a4c1b9d3f2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'messages',
        sa.Column('attachment_filename', sa.String(length=255), nullable=True),
    )
    op.add_column(
        'messages',
        sa.Column('attachment_path', sa.String(length=500), nullable=True),
    )
    op.add_column(
        'messages',
        sa.Column('attachment_size', sa.Integer(), nullable=True),
    )
    op.add_column(
        'messages',
        sa.Column('attachment_mime', sa.String(length=255), nullable=True),
    )


def downgrade() -> None:
    op.drop_column('messages', 'attachment_mime')
    op.drop_column('messages', 'attachment_size')
    op.drop_column('messages', 'attachment_path')
    op.drop_column('messages', 'attachment_filename')
