from app.llm.client import LLMClient
from app.models.project_intelligence import ProjectIntelligence


class ProjectIntelligenceAgent:

    def __init__(self):
        self.llm = LLMClient()

    def extract(self, title: str, text: str):

        prompt = f"""
Extract project-level intelligence from this Architectural Digest India
interior design project article (residential, commercial, hospitality, restaurant, etc.).

ARTICLE TITLE:
{title}

ARTICLE:
{text[:5000]}

Extract ONLY information explicitly supported by the article.

Keep every list concise. Maximum 5 items per list.
Do not explain anything outside the JSON.
Return the complete JSON object.

Return valid JSON:

{{
  "project_name": null,
  "home_type": null,
  "location": null,
  "project_size": null,
  "completion_year": null,

  "homeowner": {{
    "name": null,
    "profession": null,
    "industry": null,
    "city": null,
    "country": null,
    "public_profile_mentioned": null
  }},

  "designer": {{
    "name": null,
    "studio": null,
    "project_role": null,
    "city": null,
    "website": null,
    "project_mention": null
  }},

  "flooring": [],
  "furniture": [],
  "decor": [],
  "textile_elements": [],
  "sourcing_notes": []
}}
"""

        response = self.llm.generate(
            system_prompt="You are a precise architectural project intelligence extraction agent.",
            user_prompt=prompt,
        )

        from app.utils.json_cleaner import clean_and_parse_json
        data = clean_and_parse_json(response)
        return ProjectIntelligence.model_validate(data)