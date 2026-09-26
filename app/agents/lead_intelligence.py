from app.agents.enrichment_gate import (
    decide_enrichment_action,
)
from app.agents.freshness_manager import (
    get_freshness_status,
)
from app.agents.lead_scorer import (
    calculate_lead_score,
)
from app.agents.rug_scorer import (
    calculate_rug_opportunity_score,
)
from app.models.lead_intelligence import (
    LeadIntelligence,
)


class LeadIntelligenceAgent:

    def analyze(
        self,
        designer_name: str | None,
        studio_name: str | None,
        last_enriched_at,
        featured_in_ad: bool = False,
        luxury_residence: bool = False,
        rug: dict | None = None,
        supplier_mentioned: bool = False,
        multiple_projects: bool = False,
        active_social: bool = False,
        contact_data: bool = False,
    ) -> LeadIntelligence:

        # -----------------------------------------
        # 1. Determine freshness
        # -----------------------------------------

        freshness_status = get_freshness_status(
            last_enriched_at
        )

        # -----------------------------------------
        # 2. Decide enrichment action
        # -----------------------------------------

        enrichment_action = decide_enrichment_action(
            freshness_status
        )

        # -----------------------------------------
        # 3. Calculate lead score
        # -----------------------------------------

        rug = rug or {}

        rug_used = rug.get("rug_used")

        rug_mentioned = (
            rug_used is True
            or str(rug_used).strip().lower() in ("yes", "true", "1")
        )

        lead_score = calculate_lead_score(
            featured_in_ad=featured_in_ad,
            luxury_residence=luxury_residence,
            rug_mentioned=rug_mentioned,
            supplier_mentioned=supplier_mentioned,
            multiple_projects=multiple_projects,
            active_social=active_social,
            contact_data=contact_data,
        )

        # -----------------------------------------
        # 4. Calculate rug opportunity score
        # -----------------------------------------

        rug_opportunity_score = (
            calculate_rug_opportunity_score(rug)
        )

        # -----------------------------------------
        # 5. Build final intelligence record
        # -----------------------------------------

        return LeadIntelligence(
            designer_name=designer_name,
            studio_name=studio_name,
            freshness_status=freshness_status,
            enrichment_action=enrichment_action,
            lead_score=lead_score,
            rug_opportunity_score=rug_opportunity_score,
            rug_used=rug.get("rug_used"),
            supplier_mentioned=supplier_mentioned,
            multiple_projects=multiple_projects,
            active_social=active_social,
            contact_data=contact_data,
        )