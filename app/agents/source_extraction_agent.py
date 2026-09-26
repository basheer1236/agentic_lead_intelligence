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

        for website in source.get("websites", []):
            fields.append(
                ExtractedField(
                    field="website",
                    value=website,
                    source_url=source_url,
                    source_type=source_type,
                    evidence_text=f"Website link found on source: {website}",
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
                if val.verification_status in ("VERIFIED", "BLOCKED_OR_UNVERIFIED", "UNVERIFIED") and val.is_profile_type:
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

        raw_response = self.llm.generate(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt,
        )

        data = _extract_json(raw_response)

        semantic_result = SourceExtractionResult.model_validate(data)

        # ---------------------------------------------------------
        # Merge deterministic + semantic fields
        # ---------------------------------------------------------

        all_fields = fields + semantic_result.fields

        return SourceExtractionResult(
            source_url=source_url,
            source_type=source_type,
            fields=all_fields,
        )