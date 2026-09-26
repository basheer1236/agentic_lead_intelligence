from app.models.designer_enrichment import (
    DesignerEnrichment,
    Evidence,
)
from app.agents.designer_enrichment_merge import (
    merge_designer_enrichment,
)


def main():

    # -----------------------------------------
    # Primary source: AD PRO
    # -----------------------------------------
    ad_profile = DesignerEnrichment(
        studio_name="Ekaa - The Design Collective",
        website="https://www.ekaathedesigncollective.com",
        email="matt@ekaathedesigncollective.com",
        instagram_url="https://www.instagram.com/ekaa.designcollective",
        evidence=[
            Evidence(
                field="email",
                value="matt@ekaathedesigncollective.com",
                source_url="https://www.architecturaldigest.in/adpro/directory/profile/ekaa-the-design-collective/",
                source_type="ad_pro_directory",
                confidence=1.0,
            )
        ],
    )

    # -----------------------------------------
    # Secondary source: website
    # -----------------------------------------
    website_profile = DesignerEnrichment(
        studio_name="Ekaa - The Design Collective",
        city="Mumbai",
        country="India",
        company_description="Interior design studio",
        facebook_url="https://www.facebook.com/example",
        evidence=[
            Evidence(
                field="city",
                value="Mumbai",
                source_url="https://www.ekaathedesigncollective.com",
                source_type="website",
                confidence=0.9,
            ),
            Evidence(
                field="company_description",
                value="Interior design studio",
                source_url="https://www.ekaathedesigncollective.com",
                source_type="website",
                confidence=0.9,
            ),
        ],
    )

    # -----------------------------------------
    # Merge
    # -----------------------------------------
    result = merge_designer_enrichment(
        ad_profile,
        website_profile,
    )

    print("\nMERGED DESIGNER PROFILE")
    print("=" * 50)

    print("Studio:", result.studio_name)
    print("Website:", result.website)
    print("Email:", result.email)
    print("City:", result.city)
    print("Country:", result.country)
    print("Instagram:", result.instagram_url)
    print("Facebook:", result.facebook_url)
    print("Description:", result.company_description)

    print("\nEVIDENCE")
    for evidence in result.evidence:
        print(
            f"- {evidence.field}: "
            f"{evidence.value} "
            f"[{evidence.source_type}] "
            f"confidence={evidence.confidence}"
        )


if __name__ == "__main__":
    main()