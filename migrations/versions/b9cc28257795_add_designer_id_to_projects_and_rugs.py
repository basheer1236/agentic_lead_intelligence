"""add designer_id to projects and rugs

Revision ID: b9cc28257795
Revises: 3d31adfc375d
Create Date: 2026-09-24 11:58:14.217128

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b9cc28257795'
down_revision: Union[str, Sequence[str], None] = '3d31adfc375d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Add designer_id columns
    op.add_column('projects', sa.Column('designer_id', sa.Integer(), sa.ForeignKey('designers.id'), nullable=True))
    op.add_column('rugs', sa.Column('designer_id', sa.Integer(), sa.ForeignKey('designers.id'), nullable=True))

    # 2. Backfill projects.designer_id using deterministic match
    op.execute("""
        UPDATE projects p
        SET designer_id = d.id
        FROM designers d
        WHERE p.designer_id IS NULL
          AND p.designer_website IS NOT NULL
          AND p.designer_website = d.website;
    """)

    op.execute("""
        UPDATE projects p
        SET designer_id = d.id
        FROM designers d
        WHERE p.designer_id IS NULL
          AND p.designer_name IS NOT NULL
          AND d.normalized_name IS NOT NULL
          AND LOWER(TRIM(p.designer_name)) = d.normalized_name;
    """)

    op.execute("""
        UPDATE projects p
        SET designer_id = d.id
        FROM designers d
        WHERE p.designer_id IS NULL
          AND p.designer_name IS NOT NULL
          AND LOWER(TRIM(p.designer_name)) = LOWER(TRIM(d.designer_name));
    """)

    # 3. Backfill rugs.designer_id from projects.designer_id
    op.execute("""
        UPDATE rugs r
        SET designer_id = p.designer_id
        FROM projects p
        WHERE r.project_id = p.id
          AND p.designer_id IS NOT NULL;
    """)


def downgrade() -> None:
    op.drop_column('rugs', 'designer_id')
    op.drop_column('projects', 'designer_id')
