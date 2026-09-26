"""canonical designer identity backfill

Revision ID: d4e5f6a7b8c9
Revises: b9cc28257795
Create Date: 2026-09-24 15:35:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.orm import Session
from app.utils.name_normalizer import normalize_designer_name

# revision identifiers, used by Alembic.
revision: str = 'd4e5f6a7b8c9'
down_revision: Union[str, Sequence[str], None] = 'b9cc28257795'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    session = Session(bind=bind)

    # 1. Update canonical Record ID 4 with merged data from 5 & 41
    op.execute("""
        UPDATE designers
        SET designer_name = 'Aayush Golecha & Kushaal Jhaveri',
            normalized_name = 'aayush golecha | kushaal jhaveri',
            website = COALESCE(website, 'https://www.ekaathedesigncollective.com'),
            email = COALESCE(email, 'matt@ekaathedesigncollective.com'),
            instagram_url = COALESCE(instagram_url, 'https://www.instagram.com/ekaa.designcollective'),
            instagram_verified = TRUE,
            instagram_confidence = 0.8,
            company_description = COALESCE(company_description, 'In Mumbai, The Comma Collective lets art, colour and collected objects lead the way, creating a layered family home that rejects the idea that luxury needs to be restrained.'),
            city = COALESCE(city, 'Mumbai')
        WHERE id = 4;
    """)

    # 2. Repoint dependent records from IDs 5 and 41 to canonical ID 4
    op.execute("UPDATE projects SET designer_id = 4 WHERE designer_id IN (5, 41);")
    op.execute("UPDATE rugs SET designer_id = 4 WHERE designer_id IN (5, 41);")
    
    # Repoint sources table if designer_id column exists
    try:
        op.execute("UPDATE sources SET designer_id = 4 WHERE designer_id IN (5, 41);")
    except Exception:
        pass

    # 3. Safely delete duplicate retired records 5 and 41 (Preserving ID 25!)
    op.execute("DELETE FROM designers WHERE id IN (5, 41);")

    # 4. Canonicalize normalized_name for all remaining designers in table
    designers = session.execute(sa.text("SELECT id, designer_name FROM designers")).fetchall()
    for row in designers:
        d_id, d_name = row[0], row[1]
        canon = normalize_designer_name(d_name)
        if canon:
            session.execute(
                sa.text("UPDATE designers SET normalized_name = :canon WHERE id = :id"),
                {"canon": canon, "id": d_id}
            )

    session.commit()


def downgrade() -> None:
    pass
