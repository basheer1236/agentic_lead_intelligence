import json
import re

from app.llm.client import LLMClient
from app.models.public_research import (
    PublicResearchResult,
)


SYSTEM_PROMPT = """
You are a public-source research analyst.

Your job is to determine whether web search results
belong to the target interior designer or design studio.

IMPORTANT RULES:

1. Use ONLY information contained in the supplied
   search result title, URL, and snippet.

2. Do NOT invent information.

3. Do NOT assume two companies are the same because
   their names are similar.

4. A source is relevant only when there is reasonable
   evidence that it refers to the target designer/studio.

5. Prefer these sources when relevant:
   - official company websites
   - Architectural Digest
   - LinkedIn
   - Instagram
   - Facebook
   - recognized design directories

6. Similar names from different cities must be treated
   as potentially different entities.

7. Pay attention to:
   - designer name
   - studio name
   - city
   - website/domain
   - source context

8. Return ONLY valid JSON.

9. Do NOT use markdown code fences.

10. Do NOT add explanations before or after the JSON.

11. Confidence must be between 0 and 1.

12. If there is insufficient evidence to determine
    whether a source belongs to the target entity,
    mark it as irrelevant or use a low confidence value.

For every supplied search result, provide:
- title
- url
- source_type
- relevance
- confidence
- reason
- evidence
"""


def _extract_json(raw_response: str) -> dict:
    """
    Safely extract a JSON object from an LLM response.

    Handles:
    - plain JSON
    - ```json ... ```
    - accidental text before JSON
    - accidental text after JSON
    """

    if not raw_response:
        raise ValueError(
            "LLM returned an empty response."
        )

    text = raw_response.strip()

    # ---------------------------------------------------------
    # Remove markdown code fences
    # ---------------------------------------------------------

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

    from app.utils.json_cleaner import clean_and_parse_json
    parsed = clean_and_parse_json(text)
    if not parsed:
        return {"designer_name": designer_name, "studio_name": studio_name, "sources": []}
    return parsed


class PublicResearchAgent:

    def __init__(self):

        self.llm = LLMClient()

    def research(
        self,
        designer_name: str,
        studio_name: str,
        search_results: list[dict],
    ) -> PublicResearchResult:

        # -----------------------------------------------------
        # Handle empty search results
        # -----------------------------------------------------

        if not search_results:

            return PublicResearchResult(
                designer_name=designer_name,
                studio_name=studio_name,
                sources=[],
            )

        # -----------------------------------------------------
        # Convert search results into LLM-readable context
        # -----------------------------------------------------

        formatted_results = []

        for index, result in enumerate(
            search_results,
            start=1,
        ):

            formatted_results.append(
                (
                    f"RESULT {index}\n"
                    f"Title: {result.get('title', '')}\n"
                    f"URL: {result.get('url', '')}\n"
                    f"Snippet: {result.get('snippet', '')}\n"
                    f"Source Type: "
                    f"{result.get('source_type', '')}\n"
                )
            )

        results_text = "\n".join(
            formatted_results
        )

        # -----------------------------------------------------
        # User prompt
        # -----------------------------------------------------

        user_prompt = f"""
Target designer:
{designer_name}

Target studio:
{studio_name}

Below are public web search results.

Analyze EACH result and determine whether it actually
belongs to the target designer or studio.

SEARCH RESULTS
==============

{results_text}

ENTITY RESOLUTION RULES
=======================

The target entity is:

Designer:
{designer_name}

Studio:
{studio_name}

Use the following signals:

1. Exact or near-exact studio name.
2. Designer name appearing in the result.
3. Matching city or location.
4. Matching official website/domain.
5. Matching social media handle.
6. Context indicating the same design practice.

Be conservative.

For example:

Target:
"Ekaa - The Design Collective"

A result for:
"Ekaa Designs"
in Pune

should NOT automatically be considered the same company.

Return every supplied search result in the sources array.

Return ONLY this JSON:

{{
    "designer_name": "{designer_name}",
    "studio_name": "{studio_name}",
    "sources": [
        {{
            "title": "result title",
            "url": "result url",
            "source_type": "public_web_search",
            "relevance": true,
            "confidence": 0.95,
            "reason": "Why this source belongs or does not belong to the target entity.",
            "evidence": "Specific evidence from the supplied title or snippet."
        }}
    ]
}}
"""

        # -----------------------------------------------------
        # Call LLM
        # -----------------------------------------------------

        raw_response = self.llm.generate(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt,
        )

        # -----------------------------------------------------
        # Debug raw response
        # -----------------------------------------------------

        print(
            "\n[PublicResearch] Raw LLM response:"
        )

        print("-" * 70)

        print(raw_response)

        print("-" * 70)

        # -----------------------------------------------------
        # Extract JSON
        # -----------------------------------------------------

        data = _extract_json(
            raw_response
        )

        # -----------------------------------------------------
        # Validate response with Pydantic
        # -----------------------------------------------------

        try:

            result = PublicResearchResult.model_validate(
                data
            )

        except Exception as exc:

            raise ValueError(
                "Public Research Agent returned "
                "invalid structured data.\n\n"
                f"Parsed data:\n{data}"
            ) from exc

        return result