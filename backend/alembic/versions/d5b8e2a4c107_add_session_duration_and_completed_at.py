"""Add duration_minutes and completed_at to learning_sessions

Revision ID: d5b8e2a4c107
Revises: c9a1d3f7b204
Create Date: 2026-10-29 23:50:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd5b8e2a4c107'
down_revision: Union[str, Sequence[str], None] = 'c9a1d3f7b204'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'learning_sessions',
        sa.Column(
            'duration_minutes',
            sa.Integer(),
            nullable=False,
            server_default='60',
        ),
    )
    op.add_column(
        'learning_sessions',
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column('learning_sessions', 'completed_at')
    op.drop_column('learning_sessions', 'duration_minutes')
