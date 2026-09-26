from app.storage.database import SessionLocal
from app.storage.repositories.designer_repository import DesignerRepository


def main():
    db = SessionLocal()

    try:
        designer = DesignerRepository.create(
            db=db,
            designer_name="Test Designer",
            studio_name="Test Studio",
            normalized_name="test designer",
            website="https://example.com",
            city="Mumbai",
            country="India",
            email="test@example.com",
        )

        print("Designer created:")
        print("ID:", designer.id)
        print("Name:", designer.designer_name)

        found = DesignerRepository.get_by_id(
            db,
            designer.id
        )

        print("\nDesigner found by ID:")
        print("ID:", found.id if found else None)
        print("Name:", found.designer_name if found else None)

        by_name = DesignerRepository.get_by_normalized_name(
            db,
            "test designer"
        )

        print("\nDesigner found by normalized name:")
        print("ID:", by_name.id if by_name else None)

        by_website = DesignerRepository.get_by_website(
            db,
            "https://example.com"
        )

        print("\nDesigner found by website:")
        print("ID:", by_website.id if by_website else None)

    finally:
        db.close()


if __name__ == "__main__":
    main()