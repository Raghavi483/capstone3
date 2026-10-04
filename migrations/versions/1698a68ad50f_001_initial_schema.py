"""001_initial_schema

Revision ID: 1698a68ad50f
Revises: 
Create Date: 2026-10-04 15:54:57.363490

"""
from typing import Sequence, Union
import sys
from pathlib import Path
from alembic import op
import sqlalchemy as sa

# Ensure root in sys.path
root_dir = str(Path(__file__).resolve().parent.parent.parent)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from src.repositories.database import Base
from src.repositories import models

# revision identifiers, used by Alembic.
revision: str = '1698a68ad50f'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - creates all MediCard core tables."""
    bind = op.get_bind()
    Base.metadata.create_all(bind=bind)


def downgrade() -> None:
    """Downgrade schema - drops all MediCard core tables."""
    bind = op.get_bind()
    Base.metadata.drop_all(bind=bind)
