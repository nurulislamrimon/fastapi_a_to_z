"""add password_hash to users

Revision ID: 9f2c1a8b3d4e
Revises: 1576e4015ffd
Create Date: 2026-09-06 15:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9f2c1a8b3d4e'
down_revision: Union[str, Sequence[str], None] = '1576e4015ffd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        'users',
        sa.Column('password_hash', sa.String(length=128), nullable=False, server_default=''),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('users', 'password_hash')