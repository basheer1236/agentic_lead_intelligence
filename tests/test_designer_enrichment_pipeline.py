from app.agents.designer_enrichment_pipeline import (
    DesignerEnrichmentPipeline,
)


sources = [

    {
        "requested_url": "https://example.com",
        "final_url": "https://example.com",
        "source_type": "official_website",

        "text": """
        Ekaa - The Design Collective is an interior
        design studio based in Mumbai, India.

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
    },

    {
        "requested_url": "https://www.linkedin.com/company/example",
        "final_url": "https://www.linkedin.com/company/example",
        "source_type": "linkedin",

        "text": """
        Ekaa - The Design Collective
        Mumbai, Maharashtra

        Interior Design
        """,

        "emails": [],

        "phones": [],

        "websites": [],

        "social": {
            "linkedin": [
                "https://www.linkedin.com/company/example"
            ],
            "instagram": [],
            "facebook": [],
            "youtube": [],
        },
    },
]


pipeline = DesignerEnrichmentPipeline()

result = pipeline.process_sources(
    designer_name="Matt Thannimoottil",
    studio_name="Ekaa - The Design Collective",
    sources=sources,
)


print("\nFINAL DESIGNER PROFILE\n")

print("Designer:", result.designer_name)
print("Studio:", result.studio_name)
print("Website:", result.website)
print("Email:", result.email)
print("City:", result.city)
print("Country:", result.country)
print("Description:", result.company_description)
print("LinkedIn:", result.linkedin_url)
print("Instagram:", result.instagram_url)

print("\nEVIDENCE\n")

for evidence in result.evidence:

    print(
        f"- {evidence.field}: "
        f"{evidence.value} "
        f"| {evidence.source_type} "
        f"| confidence={evidence.confidence}"
    )