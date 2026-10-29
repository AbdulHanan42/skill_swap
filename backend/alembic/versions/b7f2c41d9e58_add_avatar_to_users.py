"""Add avatar column to users

Revision ID: b7f2c41d9e58
Revises: 5dd550648c46
Create Date: 2026-10-29 15:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b7f2c41d9e58'
down_revision: Union[str, Sequence[str], None] = '5dd550648c46'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('avatar', sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column('users', 'avatar')
