from app.llm.client import LLMClient
from app.models.relevance import RelevanceResult


class RelevanceAgent:

    def __init__(self):
        self.llm = LLMClient()

    def classify(self, title: str, description: str, text: str):
        prompt = f"""
Determine whether this Architectural Digest India article
is a relevant interior-design project (residential, commercial, hospitality, restaurant, cafe, office, etc.).

Relevant examples:
- Residential spaces (Apartment, House, Villa, Residence, Penthouse, Bungalow, Mansion)
- Commercial & Hospitality spaces (Restaurant, Cafe, Hotel, Bar, Office, Retail, Store, Retreat, Lounge)
- Interior design transformations, renovations, or refurbishments

Not relevant:
- Product buying guides / furniture reviews without a featured space
- Fashion or lifestyle gossip without interior spaces
- Event or awards announcements without a featured design project

Article title:
{title}

Description:
{description}

Article text:
{text[:12000]}

Return ONLY valid JSON:

{{
  "is_relevant": true,
  "confidence": 0.95,
  "article_type": "interior_design_project",
  "reason": "Short explanation"
}}
"""

        response = self.llm.generate(
            system_prompt="You are a precise article classification agent.",
            user_prompt=prompt,
        )

        from app.utils.json_cleaner import clean_and_parse_json
        data = clean_and_parse_json(response)
        return RelevanceResult.model_validate(data)