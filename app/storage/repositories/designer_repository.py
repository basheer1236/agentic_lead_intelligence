from sqlalchemy import select
from sqlalchemy.orm import Session

from app.storage.models.designer import DesignerDB


class DesignerRepository:

    @staticmethod
    def create(
        db: Session,
        designer_name: str,
        studio_name: str | None = None,
        normalized_name: str | None = None,
        website: str | None = None,
        address: str | None = None,
        city: str | None = None,
        country: str | None = None,
        contact: str | None = None,
        email: str | None = None,
        company_description: str | None = None,
        linkedin_url: str | None = None,
        instagram_url: str | None = None,
        facebook_url: str | None = None,
        youtube_url: str | None = None,
        linkedin_verified: bool | None = False,
        instagram_verified: bool | None = False,
        linkedin_confidence: float | None = 0.0,
        instagram_confidence: float | None = 0.0,
        last_enriched_at=None,
    ):
        designer = DesignerDB(
            designer_name=designer_name,
            studio_name=studio_name,
            normalized_name=normalized_name,
            website=website,
            address=address,
            city=city,
            country=country,
            contact=contact,
            email=email,
            company_description=company_description,
            linkedin_url=linkedin_url,
            instagram_url=instagram_url,
            facebook_url=facebook_url,
            youtube_url=youtube_url,
            linkedin_verified=linkedin_verified,
            instagram_verified=instagram_verified,
            linkedin_confidence=linkedin_confidence,
            instagram_confidence=instagram_confidence,
            last_enriched_at=last_enriched_at,
        )

        db.add(designer)
        db.commit()
        db.refresh(designer)

        return designer

    @staticmethod
    def get_by_id(
        db: Session,
        designer_id: int
    ) -> DesignerDB | None:

        statement = select(DesignerDB).where(
            DesignerDB.id == designer_id
        )

        return db.scalar(statement)

    @staticmethod
    def get_by_normalized_name(
        db: Session,
        normalized_name: str
    ) -> DesignerDB | None:

        statement = select(DesignerDB).where(
            DesignerDB.normalized_name == normalized_name
        )

        return db.scalar(statement)

    @staticmethod
    def get_by_website(
        db: Session,
        website: str
    ) -> DesignerDB | None:

        statement = select(DesignerDB).where(
            DesignerDB.website == website
        )

        return db.scalar(statement)

    @staticmethod
    def get_by_studio_and_canonical_tokens(
        db: Session,
        studio_name: str | None,
        canonical_name: str
    ) -> DesignerDB | None:

        if not studio_name or not canonical_name:
            return None

        statement = select(DesignerDB).where(
            DesignerDB.studio_name.ilike(studio_name.strip()),
            DesignerDB.normalized_name == canonical_name
        )

        return db.scalar(statement)