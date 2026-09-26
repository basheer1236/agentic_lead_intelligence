from app.agents.source_extraction_agent import SourceExtractionAgent


source = {
    "requested_url": "https://example.com",
    "final_url": "https://example.com",
    "source_type": "official_website",

    "text": """
    Ekaa - The Design Collective is an interior design studio
    based in Mumbai, India.

    The studio was founded by Matt Thannimoottil.

    The company focuses on residential interior design.

    Contact:
    matt@ekaathedesigncollective.com
    """,

    "emails": [
        "matt@ekaathedesigncollective.com"
    ],

    "phones": [],

    "websites": [],

    "social": {
        "linkedin": [],
        "instagram": [
            "https://www.instagram.com/ekaa.designcollective"
        ],
        "facebook": [],
        "youtube": [],
    },
}


agent = SourceExtractionAgent()

result = agent.extract(
    designer_name="Matt Thannimoottil",
    studio_name="Ekaa - The Design Collective",
    source=source,
)

print("\nSOURCE EXTRACTION RESULT\n")

for field in result.fields:
    print(
        f"{field.field}: {field.value} "
        f"| confidence={field.confidence}"
    )
    print(f"Evidence: {field.evidence_text}")
    print()