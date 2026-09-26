from sqlalchemy import select
from sqlalchemy.orm import Session

from app.storage.models.project import ProjectDB


class ProjectRepository:

    @staticmethod
    def create(
        db: Session,
        article_id: int,
        designer_id: int | None = None,
        project_name: str | None = None,
        home_type: str | None = None,
        location: str | None = None,
        project_size: str | None = None,
        completion_year: str | None = None,
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
    ) -> ProjectDB:

        project = ProjectDB(
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

        db.add(project)
        db.commit()
        db.refresh(project)

        return project

    @staticmethod
    def get_by_id(
        db: Session,
        project_id: int
    ) -> ProjectDB | None:

        statement = select(ProjectDB).where(
            ProjectDB.id == project_id
        )

        return db.scalar(statement)

    @staticmethod
    def get_by_article_id(
        db: Session,
        article_id: int
    ) -> list[ProjectDB]:

        statement = select(ProjectDB).where(
            ProjectDB.article_id == article_id
        )

        return list(db.scalars(statement).all())