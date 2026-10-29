"""Add requested_by_id to matches

Revision ID: c9a1d3f7b204
Revises: b7f2c41d9e58
Create Date: 2026-10-29 21:40:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c9a1d3f7b204'
down_revision: Union[str, Sequence[str], None] = 'b7f2c41d9e58'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'matches',
        sa.Column('requested_by_id', sa.Integer(), nullable=True),
    )
    op.create_foreign_key(
        'fk_matches_requested_by_id',
        'matches', 'users',
        ['requested_by_id'], ['id'],
        ondelete='SET NULL',
    )


def downgrade() -> None:
    op.drop_constraint('fk_matches_requested_by_id', 'matches', type_='foreignkey')
    op.drop_column('matches', 'requested_by_id')
