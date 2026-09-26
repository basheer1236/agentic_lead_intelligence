from app.models.designer_enrichment import DesignerEnrichment, Evidence


def merge_designer_enrichment(
    ad_profile: DesignerEnrichment,
    website_profile: DesignerEnrichment | None = None,
) -> DesignerEnrichment:

    website_profile = website_profile or DesignerEnrichment()

    merged = ad_profile.model_copy(deep=True)

    # ---------------------------------------------------------
    # Helper: use secondary source only when primary is missing
    # ---------------------------------------------------------
    def fill_if_missing(field: str):
        current_value = getattr(merged, field)
        new_value = getattr(website_profile, field)

        if not current_value and new_value:
            setattr(merged, field, new_value)

    # ---------------------------------------------------------
    # Basic profile fields
    # ---------------------------------------------------------
    fields = [
        "designer_name",
        "studio_name",
        "website",
        "address",
        "city",
        "country",
        "contact",
        "email",
        "company_description",
        "linkedin_url",
        "instagram_url",
        "facebook_url",
        "youtube_url",
    ]

    for field in fields:
        fill_if_missing(field)

    # ---------------------------------------------------------
    # Key people
    # ---------------------------------------------------------
    existing_people = {
        (
            person.name or "",
            person.linkedin_url or "",
        )
        for person in merged.key_people
    }

    for person in website_profile.key_people:
        key = (
            person.name or "",
            person.linkedin_url or "",
        )

        if key not in existing_people:
            merged.key_people.append(person)
            existing_people.add(key)

    # ---------------------------------------------------------
    # Evidence
    # ---------------------------------------------------------
    existing_evidence = {
        (
            evidence.field,
            evidence.value,
            evidence.source_url,
        )
        for evidence in merged.evidence
    }

    for evidence in website_profile.evidence:
        key = (
            evidence.field,
            evidence.value,
            evidence.source_url,
        )

        if key not in existing_evidence:
            merged.evidence.append(evidence)
            existing_evidence.add(key)

    return merged