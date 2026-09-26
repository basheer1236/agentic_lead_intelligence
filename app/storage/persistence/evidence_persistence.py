from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.models.source_extraction import ExtractedField
from app.storage.repositories.source_repository import SourceRepository


class EvidencePersistenceService:

    @staticmethod
    def save_extracted_fields(
        db: Session,
        designer_id: int,
        fields: list[ExtractedField],
    ) -> int:

        saved_count = 0

        for field in fields:
            str_val = str(field.value) if field.value is not None else None

            existing = SourceRepository.get_existing(
                db=db,
                designer_id=designer_id,
                field=field.field,
                value=str_val,
                source_url=field.source_url,
            )

            if existing:
                existing.confidence = field.confidence
                existing.evidence_text = field.evidence_text or existing.evidence_text
                existing.retrieved_at = datetime.now(timezone.utc)
                db.commit()
                db.refresh(existing)
            else:
                SourceRepository.create(
                    db=db,
                    designer_id=designer_id,
                    source_url=field.source_url,
                    source_type=field.source_type,
                    field=field.field,
                    value=str_val,
                    evidence_text=field.evidence_text,
                    confidence=field.confidence,
                )
                saved_count += 1

        return saved_count