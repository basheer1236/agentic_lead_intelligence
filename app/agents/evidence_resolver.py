from collections import defaultdict
from typing import Any

from app.models.source_extraction import ExtractedField


# Higher number = stronger source
SOURCE_PRIORITY = {
    "architectural_digest": 100,
    "ad_pro_directory": 100,
    "official_website": 90,
    "linkedin": 80,
    "instagram": 70,
    "facebook": 60,
    "youtube": 60,
    "public_web_search": 40,
    "public_web": 30,
}


def _source_priority(source_type: str) -> int:
    return SOURCE_PRIORITY.get(source_type, 20)


def _normalise_value(value: Any) -> str:
    if value is None:
        return ""

    if isinstance(value, str):
        return " ".join(value.lower().strip().split())

    return str(value).lower().strip()


def _calculate_resolution_score(
    field: ExtractedField,
) -> float:

    priority = _source_priority(field.source_type)

    # Convert source priority from 0-100
    source_score = priority / 100

    # Confidence already comes from extraction
    confidence_score = field.confidence

    # Weighted combination
    return (
        source_score * 0.6
        + confidence_score * 0.4
    )


class EvidenceResolver:

    def resolve(
        self,
        fields: list[ExtractedField],
    ) -> dict[str, dict]:

        grouped = defaultdict(list)

        for field in fields:

            if field.value is None:
                continue

            grouped[field.field].append(field)

        resolved = {}

        for field_name, claims in grouped.items():

            if not claims:
                continue

            # Sort strongest claim first
            ranked_claims = sorted(
                claims,
                key=_calculate_resolution_score,
                reverse=True,
            )

            best_claim = ranked_claims[0]

            # Count supporting claims
            best_normalized = _normalise_value(
                best_claim.value
            )

            supporting_sources = []

            for claim in ranked_claims:

                claim_normalized = _normalise_value(
                    claim.value
                )

                if claim_normalized == best_normalized:
                    supporting_sources.append(
                        {
                            "source_url": claim.source_url,
                            "source_type": claim.source_type,
                            "confidence": claim.confidence,
                            "evidence_text": claim.evidence_text,
                        }
                    )

            # Agreement bonus
            agreement_count = len(
                supporting_sources
            )

            final_confidence = min(
                1.0,
                best_claim.confidence
                + max(0, agreement_count - 1) * 0.05,
            )

            resolved[field_name] = {
                "value": best_claim.value,
                "source_url": best_claim.source_url,
                "source_type": best_claim.source_type,
                "confidence": round(
                    final_confidence,
                    3,
                ),
                "evidence_text": best_claim.evidence_text,
                "supporting_sources": supporting_sources,
                "candidate_count": len(claims),
            }

        return resolved