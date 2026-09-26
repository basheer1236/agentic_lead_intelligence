from app.storage.database import SessionLocal
from app.storage.repositories.project_repository import ProjectRepository


def main():
    db = SessionLocal()

    try:
        project = ProjectRepository.create(
            db=db,
            article_id=1,
            project_name="Test Mumbai Residence",
            home_type="Apartment",
            location="Mumbai",
            designer_name="Test Designer",
            designer_studio="Test Studio",
            flooring="Marble",
            furniture="Contemporary furniture",
            decor="Modern decor",
        )

        print("Project created:")
        print("ID:", project.id)
        print("Name:", project.project_name)

        found = ProjectRepository.get_by_id(
            db,
            project.id
        )

        print("\nProject found by ID:")
        print("ID:", found.id if found else None)
        print("Name:", found.project_name if found else None)

        projects = ProjectRepository.get_by_article_id(
            db,
            1
        )

        print("\nProjects for article:")
        print("Count:", len(projects))

    finally:
        db.close()


if __name__ == "__main__":
    main()