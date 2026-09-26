from app.agents.evidence_resolver import EvidenceResolver
from app.models.source_extraction import ExtractedField


fields = [
    ExtractedField(
        field="city",
        value="Mumbai",
        source_url="https://www.architecturaldigest.in/adpro/",
        source_type="architectural_digest",
        evidence_text="Studio based in Mumbai",
        confidence=1.0,
    ),

    ExtractedField(
        field="city",
        value="Mumbai",
        source_url="https://example-studio.com",
        source_type="official_website",
        evidence_text="Our studio is based in Mumbai",
        confidence=0.95,
    ),

    ExtractedField(
        field="city",
        value="Mumbai",
        source_url="https://linkedin.com/company/example",
        source_type="linkedin",
        evidence_text="Location: Mumbai",
        confidence=0.90,
    ),

    ExtractedField(
        field="city",
        value="Pune",
        source_url="https://random-directory.com/example",
        source_type="public_web",
        evidence_text="Pune",
        confidence=0.55,
    ),
]


resolver = EvidenceResolver()

result = resolver.resolve(fields)


print("\nEVIDENCE RESOLUTION RESULT\n")

for field, data in result.items():

    print(f"FIELD: {field}")
    print(f"VALUE: {data['value']}")
    print(f"SOURCE: {data['source_type']}")
    print(f"CONFIDENCE: {data['confidence']}")
    print(
        f"CANDIDATES: {data['candidate_count']}"
    )

    print("SUPPORTING SOURCES:")

    for source in data["supporting_sources"]:
        print(
            f"  - {source['source_type']} "
            f"| confidence={source['confidence']}"
        )

    print()