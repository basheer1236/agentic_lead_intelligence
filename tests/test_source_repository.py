from app.storage.database import SessionLocal
from app.storage.repositories.source_repository import SourceRepository


def main():
    db = SessionLocal()

    try:
        source = SourceRepository.create(
            db=db,
            designer_id=1,
            source_url="https://example.com/about",
            source_type="official_website",
            field="website",
            value="https://example.com",
            evidence_text="Visit our official studio website.",
            confidence=0.95,
        )

        print("Source created:")
        print("ID:", source.id)
        print("Field:", source.field)
        print("Confidence:", source.confidence)

        found = SourceRepository.get_by_id(
            db,
            source.id
        )

        print("\nSource found by ID:")
        print("ID:", found.id if found else None)

        designer_sources = SourceRepository.get_by_designer_id(
            db,
            1
        )

        print("\nSources for designer:")
        print("Count:", len(designer_sources))

        website_sources = SourceRepository.get_by_field(
            db,
            1,
            "website"
        )

        print("\nWebsite sources:")
        print("Count:", len(website_sources))

    finally:
        db.close()


if __name__ == "__main__":
    main()