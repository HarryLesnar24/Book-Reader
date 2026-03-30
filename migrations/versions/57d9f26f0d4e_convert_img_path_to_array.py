"""convert img_path to array

Revision ID: 57d9f26f0d4e
Revises: 6641acfbade4
Create Date: 2026-03-19 08:42:25.968528

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '57d9f26f0d4e'
down_revision: Union[str, Sequence[str], None] = '6641acfbade4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(
            """
            ALTER TABLE pages 
            ALTER COLUMN img_path TYPE VARCHAR[] 
            USING ARRAY[img_path]::VARCHAR[]
            """
        )


def downgrade() -> None:
    """Downgrade schema."""
    op.execute(
        """
        ALTER TABLE pages 
        ALTER COLUMN img_path TYPE VARCHAR 
        USING img_path[1]
        """
    )
