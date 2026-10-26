def _is_official_studio_domain(netloc: str, designer_name: str | None = None, studio_name: str | None = None) -> bool:
    if not netloc:
        return False
    netloc_clean = re.sub(r'^(www\.)', '', netloc.lower())
    non_studio = {
        "linkedin.com", "instagram.com", "facebook.com", "youtube.com",
        "architecturaldigest.in", "architecturaldigest.com", "wikipedia.org",
        "pinterest.com", "twitter.com", "x.com", "indiadesignid.com", "homegrown.co.in",
        "outlookindia.com", "vogue.in", "elledecor.in", "f6s.com", "rocketreach.co"
    }
    if any(ns in netloc_clean for ns in non_studio):
        return False
    tokens = set()
    for name in (studio_name, designer_name):
        if name:
            for t in re.split(r'[^a-zA-Z0-9]', name.lower()):
                if len(t) >= 4 and t not in ("studio", "design", "designs", "architects", "architecture", "interior", "interiors", "group", "the", "and"):
                    tokens.add(t)
    if not tokens:
        return False
    return any(t in netloc_clean for t in tokens)

import json
import re

from app.llm.client import LLMClient
from app.models.source_extraction import (
    ExtractedField,
    SourceExtractionResult,
)


SYSTEM_PROMPT = """
You are a public-source information extraction agent.

Your job is to extract designer/company information from supplied
public web source content.

STRICT RULES:

1. Use ONLY information explicitly present in the supplied source.
2. Never invent, infer, or guess missing information.
3. Do not treat similar company names as the same company.
4. Extract only information relevant to the requested designer/studio.
5. Every extracted field must include evidence from the source.
6. Confidence must reflect how clearly the source supports the field.
7. If information is not present, do not create a field for it.
8. Return ONLY valid JSON.
"""


def _extract_json(raw_response: str) -> dict:
    if not raw_response:
        raise ValueError("Empty LLM response.")

    text = raw_response.strip()

    text = re.sub(
        r"^```json\s*",
        "",
        text,
        flags=re.IGNORECASE,
    )

    text = re.sub(
        r"^```\s*",
        "",
        text,
    )

    text = re.sub(
        r"\s*```$",
        "",
        text,
    )

    text = text.strip()

    try:
        return json.loads(text, strict=False)
    except json.JSONDecodeError:
        pass

    start = text.find("{")
    end = text.rfind("}")

    if start == -1:
        raise ValueError("No valid JSON object found.")

    if end == -1 or end <= start:
        json_str = text[start:] + "}"
    else:
        json_str = text[start:end + 1]

    try:
        return json.loads(json_str, strict=False)
    except json.JSONDecodeError:
        json_str = re.sub(r",\s*([}\]])", r"\1", json_str)
        try:
            return json.loads(json_str, strict=False)
        except json.JSONDecodeError:
            # If closing braces/brackets missing from LLM truncation, append closing chars
            if json_str.count("[") > json_str.count("]"):
                json_str += "]"
            if json_str.count("{") > json_str.count("}"):
                json_str += "}"
            return json.loads(json_str, strict=False)


class SourceExtractionAgent:

    def __init__(self):
        self.llm = LLMClient()

    def extract(
        self,
        designer_name: str,
        studio_name: str | None,
        source: dict,
    ) -> SourceExtractionResult:

        source_url = source.get("final_url") or source.get("requested_url")
        source_type = source.get("source_type", "public_web")

        fields = []

        # ---------------------------------------------------------
        # Deterministic extraction
        # ---------------------------------------------------------

        for email in source.get("emails", []):
            fields.append(
                ExtractedField(
                    field="email",
                    value=email,
                    source_url=source_url,
                    source_type=source_type,
                    evidence_text=f"Email found on source: {email}",
                    confidence=1.0,
                )
            )

        for phone in source.get("phones", []):
            fields.append(
                ExtractedField(
                    field="contact",
                    value=phone,
                    source_url=source_url,
                    source_type=source_type,
                    evidence_text=f"Phone number found on source: {phone}",
                    confidence=1.0,
                )
            )

        from urllib.parse import urlparse
        social_and_portal_domains = {
            "linkedin.com", "instagram.com", "facebook.com", "youtube.com",
            "threads.com", "threads.net", "twitter.com", "x.com", "linktr.ee",
            "linktree.com", "pinterest.com", "behance.net", "vimeo.com",
            "architecturaldigest.in", "wikipedia.org", "indiadesignid.com"
        }
        for website in source.get("websites", []):
            parsed_w = urlparse(website)
            netloc_w = parsed_w.netloc.lower()
            if any(gd in netloc_w for gd in social_and_portal_domains):
                continue
            if _is_official_studio_domain(netloc_w, designer_name, studio_name):
                root_w = f"{parsed_w.scheme or 'https'}://{parsed_w.netloc}"
                fields.append(
                    ExtractedField(
                        field="website",
                        value=root_w,
                        source_url=source_url,
                        source_type="official_website",
                        evidence_text=f"Official studio root website identified: {root_w}",
                        confidence=1.0,
                    )
                )

        from app.utils.url_validator import validate_social_url

        social = source.get("social", {})

        social_mapping = {
            "linkedin": "linkedin_url",
            "instagram": "instagram_url",
            "facebook": "facebook_url",
            "youtube": "youtube_url",
        }

        for social_type, field_name in social_mapping.items():
            for social_url in social.get(social_type, []):
                val = validate_social_url(
                    url=social_url,
                    designer_name=designer_name,
                    studio_name=studio_name,
                    platform_target=social_type
                )
                # Media blacklist guard: Never attribute known media / magazine accounts to designers
                media_bl = {"dezeen", "architecturaldigest", "vogue", "elledecor", "goodhomes", "archdaily", "forbes"}
                clean_soc_u = social_url.lower().replace("-", "").replace("_", "").replace(".", "")
                if any(m in clean_soc_u for m in media_bl):
                    continue

                # On non-official sites, require VERIFIED identity match
                is_official = (source_type == "official_website")
                status_ok = (val.verification_status == "VERIFIED") or (is_official and val.verification_status in ("BLOCKED_OR_UNVERIFIED", "UNVERIFIED"))
                if status_ok and val.is_profile_type:
                    fields.append(
                        ExtractedField(
                            field=field_name,
                            value=val.normalized_url or social_url,
                            source_url=source_url,
                            source_type=source_type,
                            evidence_text=(
                                f"{social_type.title()} link found ({val.verification_status}): "
                                f"{val.normalized_url or social_url}"
                            ),
                            confidence=val.confidence,
                        )
                    )

        # ---------------------------------------------------------
        # Self-URL Direct Validation (Profile / Official Website)
        # ---------------------------------------------------------
        from urllib.parse import urlparse
        urls_to_inspect = []
        for k in ("requested_url", "final_url", "url"):
            val_u = source.get(k)
            if val_u and val_u not in urls_to_inspect:
                urls_to_inspect.append(val_u)

        for check_url in urls_to_inspect:
            lower_u = check_url.lower()

            # Check if this source URL is itself a verified social profile (handles login wall)
            for social_type, field_name in social_mapping.items():
                if f"{social_type}.com/" in lower_u:
                    val = validate_social_url(
                        url=check_url,
                        designer_name=designer_name,
                        studio_name=studio_name,
                        platform_target=social_type
                    )
                    if val.is_profile_type and val.verification_status in ("VERIFIED", "BLOCKED_OR_UNVERIFIED", "UNVERIFIED"):
                        fields.append(
                            ExtractedField(
                                field=field_name,
                                value=val.normalized_url or check_url,
                                source_url=source_url,
                                source_type=source_type,
                                evidence_text=f"Direct {social_type.title()} profile identified: {val.normalized_url or check_url}",
                                confidence=val.confidence or 0.95,
                            )
                        )

            # Check if this source URL is the studio's official website
            parsed_src = urlparse(check_url)
            netloc = parsed_src.netloc.lower()
            if netloc and _is_official_studio_domain(netloc, designer_name, studio_name):
                root_site = f"{parsed_src.scheme or 'https'}://{parsed_src.netloc}"
                fields.append(
                    ExtractedField(
                        field="website",
                        value=root_site,
                        source_url=source_url,
                        source_type="official_website",
                        evidence_text=f"Official studio root website identified: {root_site}",
                        confidence=1.0,
                    )
                )

        # ---------------------------------------------------------
        # Semantic extraction
        # ---------------------------------------------------------

        text = source.get("text", "")

        if not text:
            return SourceExtractionResult(
                source_url=source_url,
                source_type=source_type,
                fields=fields,
            )

        # Limit input size
        text = text[:12000]

        user_prompt = f"""
Target designer:
{designer_name}

Target studio:
{studio_name or "Unknown"}

Source URL:
{source_url}

Source type:
{source_type}

Source content:
{text}

Extract ONLY information explicitly supported by this source.

Possible semantic fields:

- designer_name
- studio_name
- address
- city
- country
- company_description
- key_people

For key_people, extract:
- person's name
- title
- role
- LinkedIn URL if explicitly present

For every extracted field provide:

field
value
source_url
source_type
evidence_text
confidence

Return this JSON structure:

{{
  "source_url": "...",
  "source_type": "...",
  "fields": [
    {{
      "field": "...",
      "value": "...",
      "source_url": "...",
      "source_type": "...",
      "evidence_text": "...",
      "confidence": 0.0
    }}
  ]
}}

Do not return fields that are not supported by the source.
"""

        semantic_fields = []
        try:
            raw_response = self.llm.generate(
                system_prompt=SYSTEM_PROMPT,
                user_prompt=user_prompt,
            )
            data = _extract_json(raw_response)
            semantic_result = SourceExtractionResult.model_validate(data)
            semantic_fields = semantic_result.fields
        except Exception as exc:
            print(f"[SourceExtractionAgent] LLM semantic extraction error (deterministic fields preserved): {exc}")

        # ---------------------------------------------------------
        # Merge deterministic + semantic fields
        # ---------------------------------------------------------
        all_fields = fields + semantic_fields

        return SourceExtractionResult(
            source_url=source_url,
            source_type=source_type,
            fields=all_fields,
        )