from app.agents.evidence_resolver import EvidenceResolver
from app.agents.source_extraction_agent import SourceExtractionAgent
from app.models.designer_enrichment import DesignerEnrichment, Evidence, KeyPerson


class DesignerEnrichmentPipeline:

    def __init__(self):
        self.extractor = SourceExtractionAgent()
        self.resolver = EvidenceResolver()

    def process_sources(
        self,
        designer_name: str,
        studio_name: str | None,
        sources: list[dict],
    ) -> DesignerEnrichment:

        all_fields = []

        # -----------------------------------------
        # 1. Extract fields from every source
        # -----------------------------------------

        for source in sources:

            try:
                result = self.extractor.extract(
                    designer_name=designer_name,
                    studio_name=studio_name,
                    source=source,
                )

                all_fields.extend(result.fields)

            except Exception as exc:

                print(
                    f"[EnrichmentPipeline] "
                    f"Source extraction failed: {exc}"
                )

        # -----------------------------------------
        # 2. Resolve conflicting claims
        # -----------------------------------------

        resolved = self.resolver.resolve(
            all_fields
        )

        # -----------------------------------------
        # 3. Build final designer profile
        # -----------------------------------------

        profile = DesignerEnrichment(
            designer_name=designer_name,
            studio_name=studio_name,
        )

        field_mapping = {
            "designer_name": "designer_name",
            "studio_name": "studio_name",
            "website": "website",
            "address": "address",
            "city": "city",
            "country": "country",
            "contact": "contact",
            "email": "email",
            "company_description": "company_description",
            "linkedin_url": "linkedin_url",
            "instagram_url": "instagram_url",
            "facebook_url": "facebook_url",
            "youtube_url": "youtube_url",
        }

        # -----------------------------------------
        # 4. Apply resolved scalar fields
        # -----------------------------------------

        for field_name, target_field in field_mapping.items():

            if field_name not in resolved:
                continue

            value = resolved[field_name]["value"]

            if value is not None:
                setattr(
                    profile,
                    target_field,
                    value,
                )

        # -----------------------------------------
        # 5. Validate & verify social media URLs
        # -----------------------------------------
        from app.utils.url_validator import validate_social_url

        if profile.linkedin_url:
            val = validate_social_url(
                profile.linkedin_url,
                designer_name=designer_name,
                studio_name=studio_name,
                platform_target="linkedin"
            )
            if val.verification_status in ("VERIFIED", "BLOCKED_OR_UNVERIFIED") and val.is_profile_type:
                profile.linkedin_url = val.normalized_url or profile.linkedin_url
                profile.linkedin_verified = (val.verification_status == "VERIFIED")
                profile.linkedin_confidence = val.confidence
            else:
                profile.linkedin_url = None
                profile.linkedin_verified = False
                profile.linkedin_confidence = 0.0

        if profile.instagram_url:
            val = validate_social_url(
                profile.instagram_url,
                designer_name=designer_name,
                studio_name=studio_name,
                platform_target="instagram"
            )
            if val.verification_status in ("VERIFIED", "BLOCKED_OR_UNVERIFIED") and val.is_profile_type:
                profile.instagram_url = val.normalized_url or profile.instagram_url
                profile.instagram_verified = (val.verification_status == "VERIFIED")
                profile.instagram_confidence = val.confidence
            else:
                profile.instagram_url = None
                profile.instagram_verified = False
                profile.instagram_confidence = 0.0

        # -----------------------------------------
        # 6. Convert resolved claims into evidence
        # -----------------------------------------

        for field_name, data in resolved.items():

            value = data["value"]

            if isinstance(value, (dict, list)):
                continue

            profile.evidence.append(
                Evidence(
                    field=field_name,
                    value=str(value) if value is not None else None,
                    source_url=data["source_url"],
                    source_type=data["source_type"],
                    evidence_text=data["evidence_text"],
                    confidence=data["confidence"],
                )
            )

        return profile