from app.llm.client import LLMClient
from app.models.rug_intelligence import RugIntelligence


class RugIntelligenceAgent:

    def __init__(self):
        self.llm = LLMClient()

    def analyze(self, title: str, text: str):

        prompt = f"""
Analyze this Architectural Digest India interior design project
specifically for rugs, carpets and runners.

ARTICLE TITLE:
{title}

ARTICLE:
{text[:5500]}

STRICT EXTRACTION RULES:

1. Extract ONLY information explicitly supported by the article.
2. Search for any floor-covering keywords: rug, carpet, runner, dhurrie, mat, tapestry.
3. matched_keywords = comma-separated string of floor-covering keywords found (e.g. "carpet, runner, rug").
4. designer_custom_rug = true ONLY when the article explicitly indicates that the rug, carpet, or runner was designed, custom-created, or specified by the interior designer/architect.
5. Never guess, infer, or assume missing information. If unavailable, return null.
6. Boolean fields must be true, false, or null.
7. multiple_rugs = true ONLY when the article explicitly indicates
   that more than one rug, carpet, or runner is used.
8. luxury_project = true ONLY when the article explicitly describes
   the project as luxury, high-end, premium, or equivalent.
9. Do NOT calculate opportunity_score.
   Python will calculate the score separately.
10. Keep rug_notes concise.
11. Return ONLY valid JSON. No markdown or explanations.

Return exactly this JSON structure:

{{
  "rug_used": "Yes",
  "rug_type": null,
  "rug_origin": null,
  "rug_material": null,
  "rug_supplier": null,
  "rug_brand": null,
  "handmade": null,
  "handwoven": null,
  "vintage": null,
  "custom_made": null,
  "imported": null,
  "multiple_rugs": null,
  "luxury_project": null,
  "designer_custom_rug": null,
  "matched_keywords": null,
  "room_location": null,
  "rug_notes": null
}}
"""

        response = self.llm.generate(
            system_prompt=(
                "You are a strict evidence-based rug intelligence "
                "extraction agent. Never hallucinate."
            ),
            user_prompt=prompt,
        )

        from app.utils.json_cleaner import clean_and_parse_json
        data = clean_and_parse_json(response)
        return RugIntelligence.model_validate(data)