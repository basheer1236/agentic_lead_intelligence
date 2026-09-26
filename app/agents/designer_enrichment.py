from app.models.designer_enrichment import (
    DesignerEnrichment,
    Evidence,
)


class DesignerEnrichmentAgent:
    """
    Convert verified AD PRO Directory profile data into the
    DesignerEnrichment model.

    This layer does not infer missing information.
    """

    def enrich(
        self,
        designer_name: str | None,
        studio_name: str | None,
        profile: dict,
    ) -> DesignerEnrichment:

        profile_url = profile.get(
            "profile_url"
        )

        websites = profile.get(
            "websites",
            []
        )

        emails = profile.get(
            "emails",
            []
        )

        social = profile.get(
            "social",
            {}
        )

        # ---------------------------------------------------------
        # Website
        # ---------------------------------------------------------

        website = (
            websites[0]
            if websites
            else None
        )

        # ---------------------------------------------------------
        # Email
        # ---------------------------------------------------------

        email = (
            emails[0]
            if emails
            else None
        )

        # ---------------------------------------------------------
        # Social
        # ---------------------------------------------------------

        linkedin_url = self._first(
            social.get("linkedin", [])
        )

        instagram_url = self._first(
            social.get("instagram", [])
        )

        facebook_url = self._first(
            social.get("facebook", [])
        )

        youtube_url = self._first(
            social.get("youtube", [])
        )

        # ---------------------------------------------------------
        # Evidence
        # ---------------------------------------------------------

        evidence = []

        if website:
            evidence.append(
                Evidence(
                    field="website",
                    value=website,
                    source_url=profile_url,
                    source_type="ad_pro_directory",
                    evidence_text=website,
                    confidence=1.0,
                )
            )

        if email:
            evidence.append(
                Evidence(
                    field="email",
                    value=email,
                    source_url=profile_url,
                    source_type="ad_pro_directory",
                    evidence_text=email,
                    confidence=1.0,
                )
            )

        if linkedin_url:
            evidence.append(
                Evidence(
                    field="linkedin_url",
                    value=linkedin_url,
                    source_url=profile_url,
                    source_type="ad_pro_directory",
                    evidence_text=linkedin_url,
                    confidence=1.0,
                )
            )

        if instagram_url:
            evidence.append(
                Evidence(
                    field="instagram_url",
                    value=instagram_url,
                    source_url=profile_url,
                    source_type="ad_pro_directory",
                    evidence_text=instagram_url,
                    confidence=1.0,
                )
            )

        if facebook_url:
            evidence.append(
                Evidence(
                    field="facebook_url",
                    value=facebook_url,
                    source_url=profile_url,
                    source_type="ad_pro_directory",
                    evidence_text=facebook_url,
                    confidence=1.0,
                )
            )

        if youtube_url:
            evidence.append(
                Evidence(
                    field="youtube_url",
                    value=youtube_url,
                    source_url=profile_url,
                    source_type="ad_pro_directory",
                    evidence_text=youtube_url,
                    confidence=1.0,
                )
            )

        # ---------------------------------------------------------
        # Build final enrichment object
        # ---------------------------------------------------------

        return DesignerEnrichment(
            designer_name=designer_name,
            studio_name=studio_name,
            website=website,
            email=email,
            linkedin_url=linkedin_url,
            instagram_url=instagram_url,
            facebook_url=facebook_url,
            youtube_url=youtube_url,
            evidence=evidence,
        )

    # =============================================================
    # HELPERS
    # =============================================================

    @staticmethod
    def _first(
        values: list[str],
    ) -> str | None:

        if not values:
            return None

        return values[0]