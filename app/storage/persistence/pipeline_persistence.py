from sqlalchemy.orm import Session

from app.storage.repositories.article_repository import ArticleRepository
from app.storage.repositories.project_repository import ProjectRepository
from app.storage.repositories.designer_repository import DesignerRepository
from app.storage.repositories.rug_repository import RugRepository
from app.storage.persistence.evidence_persistence import EvidencePersistenceService
from app.storage.persistence.score_persistence import ScorePersistenceService


class PipelinePersistenceService:

    @staticmethod
    def save_article(
        db: Session,
        url: str,
        title: str | None = None,
        author: str | None = None,
        summary: str | None = None,
        published_at=None,
        content_hash: str | None = None,
    ):
        article, created = ArticleRepository.get_or_create(
            db=db,
            url=url,
            content_hash=content_hash,
        )

        if title is not None:
            article.title = title

        if author is not None:
            article.author = author

        if summary is not None:
            article.summary = summary

        if published_at is not None:
            article.published_at = published_at

        db.commit()
        db.refresh(article)

        return article, created

    @staticmethod
    def save_project(
        db: Session,
        article_id: int,
        designer_id: int | None = None,
        project_name: str | None = None,
        home_type: str | None = None,
        location: str | None = None,
        project_size: str | None = None,
        completion_year: int | None = None,
        homeowner_name: str | None = None,
        homeowner_profession: str | None = None,
        homeowner_industry: str | None = None,
        homeowner_city: str | None = None,
        homeowner_country: str | None = None,
        designer_name: str | None = None,
        designer_studio: str | None = None,
        designer_role: str | None = None,
        designer_city: str | None = None,
        designer_website: str | None = None,
        flooring: str | None = None,
        furniture: str | None = None,
        decor: str | None = None,
        textile_elements: str | None = None,
        sourcing_notes: str | None = None,
    ):
        existing_list = ProjectRepository.get_by_article_id(
            db=db, article_id=article_id
        )

        if existing_list:
            project = existing_list[0]

            if designer_id is not None:
                project.designer_id = designer_id
            if project_name is not None:
                project.project_name = project_name
            if home_type is not None:
                project.home_type = home_type
            if location is not None:
                project.location = location
            if project_size is not None:
                project.project_size = project_size
            if completion_year is not None:
                project.completion_year = str(completion_year)
            if homeowner_name is not None:
                project.homeowner_name = homeowner_name
            if homeowner_profession is not None:
                project.homeowner_profession = homeowner_profession
            if homeowner_industry is not None:
                project.homeowner_industry = homeowner_industry
            if homeowner_city is not None:
                project.homeowner_city = homeowner_city
            if homeowner_country is not None:
                project.homeowner_country = homeowner_country
            if designer_name is not None:
                project.designer_name = designer_name
            if designer_studio is not None:
                project.designer_studio = designer_studio
            if designer_role is not None:
                project.designer_role = designer_role
            if designer_city is not None:
                project.designer_city = designer_city
            if designer_website is not None:
                project.designer_website = designer_website
            if flooring is not None:
                project.flooring = flooring
            if furniture is not None:
                project.furniture = furniture
            if decor is not None:
                project.decor = decor
            if textile_elements is not None:
                project.textile_elements = textile_elements
            if sourcing_notes is not None:
                project.sourcing_notes = sourcing_notes

            db.commit()
            db.refresh(project)
            return project

        project = ProjectRepository.create(
            db=db,
            article_id=article_id,
            designer_id=designer_id,
            project_name=project_name,
            home_type=home_type,
            location=location,
            project_size=project_size,
            completion_year=completion_year,
            homeowner_name=homeowner_name,
            homeowner_profession=homeowner_profession,
            homeowner_industry=homeowner_industry,
            homeowner_city=homeowner_city,
            homeowner_country=homeowner_country,
            designer_name=designer_name,
            designer_studio=designer_studio,
            designer_role=designer_role,
            designer_city=designer_city,
            designer_website=designer_website,
            flooring=flooring,
            furniture=furniture,
            decor=decor,
            textile_elements=textile_elements,
            sourcing_notes=sourcing_notes,
        )

        return project

    @staticmethod
    def save_designer(
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
        linkedin_verified: bool | None = None,
        instagram_verified: bool | None = None,
        linkedin_confidence: float | None = None,
        instagram_confidence: float | None = None,
        last_enriched_at=None,
    ):
        from app.utils.name_normalizer import normalize_designer_name

        canonical_name = normalize_designer_name(designer_name) or (normalized_name.strip().lower() if normalized_name else None)

        existing = None

        # 1. Exact canonical name match
        if canonical_name:
            existing = DesignerRepository.get_by_normalized_name(
                db=db,
                normalized_name=canonical_name,
            )

        # 2. Studio + canonical name match
        if existing is None and studio_name and canonical_name:
            existing = DesignerRepository.get_by_studio_and_canonical_tokens(
                db=db,
                studio_name=studio_name,
                canonical_name=canonical_name,
            )

        # 3. Website match
        if existing is None and website:
            existing = DesignerRepository.get_by_website(
                db=db,
                website=website,
            )

        if existing:
            designer = existing

            if studio_name is not None:
                designer.studio_name = studio_name

            if website is not None:
                designer.website = website

            if address is not None:
                designer.address = address

            if city is not None:
                designer.city = city

            if country is not None:
                designer.country = country

            if contact is not None:
                designer.contact = contact

            if email is not None:
                designer.email = email

            if company_description is not None:
                designer.company_description = company_description

            if linkedin_url is not None:
                designer.linkedin_url = linkedin_url

            if instagram_url is not None:
                designer.instagram_url = instagram_url

            if facebook_url is not None:
                designer.facebook_url = facebook_url

            if youtube_url is not None:
                designer.youtube_url = youtube_url

            if linkedin_verified is not None:
                designer.linkedin_verified = linkedin_verified

            if instagram_verified is not None:
                designer.instagram_verified = instagram_verified

            if linkedin_confidence is not None:
                designer.linkedin_confidence = linkedin_confidence

            if instagram_confidence is not None:
                designer.instagram_confidence = instagram_confidence

            if last_enriched_at is not None:
                designer.last_enriched_at = last_enriched_at

            db.commit()
            db.refresh(designer)

            return designer, False

        designer = DesignerRepository.create(
            db=db,
            designer_name=designer_name,
            studio_name=studio_name,
            normalized_name=canonical_name,
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
            linkedin_verified=linkedin_verified if linkedin_verified is not None else False,
            instagram_verified=instagram_verified if instagram_verified is not None else False,
            linkedin_confidence=linkedin_confidence if linkedin_confidence is not None else 0.0,
            instagram_confidence=instagram_confidence if instagram_confidence is not None else 0.0,
            last_enriched_at=last_enriched_at,
        )

        return designer, True

    @staticmethod
    def save_rug(
        db: Session,
        project_id: int,
        designer_id: int | None = None,
        rug_used: str | bool | None = None,
        rug_type: str | None = None,
        origin: str | None = None,
        material: str | None = None,
        supplier: str | None = None,
        brand: str | None = None,
        handmade: bool | None = None,
        handwoven: bool | None = None,
        vintage: bool | None = None,
        custom_made: bool | None = None,
        imported: bool | None = None,
        designer_custom_rug: bool | None = None,
        matched_keywords: str | None = None,
        sourcing_notes: str | None = None,
        opportunity_score: int | None = None,
    ):
        rug_used_bool = (
            bool(rug_used)
            if isinstance(rug_used, bool)
            else (str(rug_used).strip().lower() in ("yes", "true", "1") if rug_used is not None else None)
        )

        existing_list = RugRepository.get_by_project_id(
            db=db, project_id=project_id
        )

        if existing_list:
            rug = existing_list[0]
            if designer_id is not None:
                rug.designer_id = designer_id
            if rug_used is not None:
                rug.rug_used = rug_used_bool
            if rug_type is not None:
                rug.rug_type = rug_type
            if origin is not None:
                rug.origin = origin
            if material is not None:
                rug.material = material
            if supplier is not None:
                rug.supplier = supplier
            if brand is not None:
                rug.brand = brand
            if handmade is not None:
                rug.handmade = handmade
            if handwoven is not None:
                rug.handwoven = handwoven
            if vintage is not None:
                rug.vintage = vintage
            if custom_made is not None:
                rug.custom_made = custom_made
            if imported is not None:
                rug.imported = imported
            if designer_custom_rug is not None:
                rug.designer_custom_rug = designer_custom_rug
            if matched_keywords is not None:
                rug.matched_keywords = matched_keywords
            if sourcing_notes is not None:
                rug.sourcing_notes = sourcing_notes
            if opportunity_score is not None:
                rug.opportunity_score = opportunity_score

            db.commit()
            db.refresh(rug)
            return rug

        return RugRepository.create(
            db=db,
            project_id=project_id,
            designer_id=designer_id,
            rug_used=rug_used_bool,
            rug_type=rug_type,
            origin=origin,
            material=material,
            supplier=supplier,
            brand=brand,
            handmade=handmade,
            handwoven=handwoven,
            vintage=vintage,
            custom_made=custom_made,
            imported=imported,
            designer_custom_rug=designer_custom_rug,
            matched_keywords=matched_keywords,
            sourcing_notes=sourcing_notes,
            opportunity_score=opportunity_score,
        )

    @staticmethod
    def save_evidence(
        db: Session,
        designer_id: int,
        extracted_fields,
    ):
        return EvidencePersistenceService.save_extracted_fields(
            db=db,
            designer_id=designer_id,
            fields=extracted_fields,
        )

    @staticmethod
    def save_scores(
        db: Session,
        project_id: int,
        lead_score: int | None,
        rug_opportunity_score: int | None,
    ):
        return ScorePersistenceService.save_scores(
            db=db,
            project_id=project_id,
            lead_score=lead_score,
            rug_opportunity_score=rug_opportunity_score,
        )