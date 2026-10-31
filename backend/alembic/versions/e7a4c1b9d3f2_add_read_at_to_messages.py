"""Add read_at to messages so unread counts survive a reload

Revision ID: e7a4c1b9d3f2
Revises: d5b8e2a4c107
Create Date: 2026-10-30 14:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e7a4c1b9d3f2'
down_revision: Union[str, Sequence[str], None] = 'd5b8e2a4c107'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'messages',
        sa.Column('read_at', sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column('messages', 'read_at')
