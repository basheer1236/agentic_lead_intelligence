from app.storage.database import SessionLocal
from app.storage.persistence.evidence_persistence import (
    EvidencePersistenceService,
)
from app.models.source_extraction import ExtractedField


def main():
    db = SessionLocal()

    try:
        fields = [
            ExtractedField(
                field="email",
                value="test@example.com",
                source_url="https://example.com/contact",
                source_type="official_website",
                evidence_text="Contact us at test@example.com",
                confidence=0.95,
            ),
            ExtractedField(
                field="city",
                value="Mumbai",
                source_url="https://example.com/about",
                source_type="official_website",
                evidence_text="Our studio is based in Mumbai.",
                confidence=0.90,
            ),
        ]

        count = EvidencePersistenceService.save_extracted_fields(
            db=db,
            designer_id=1,
            fields=fields,
        )

        print("Evidence records saved:", count)

    finally:
        db.close()


if __name__ == "__main__":
    main()