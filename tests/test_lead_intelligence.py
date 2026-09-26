from datetime import datetime, timedelta, timezone

from app.agents.lead_intelligence import (
    LeadIntelligenceAgent,
)


agent = LeadIntelligenceAgent()


rug = {
    "rug_used": "Yes",
    "handmade": True,
    "custom_made": True,
    "luxury_project": True,
    "multiple_rugs": True,
}


result = agent.analyze(
    designer_name="Matt Thannimoottil",
    studio_name="Ekaa - The Design Collective",

    last_enriched_at=(
        datetime.now(timezone.utc)
        - timedelta(days=60)
    ),

    featured_in_ad=True,
    luxury_residence=True,

    rug=rug,

    supplier_mentioned=True,
    multiple_projects=True,
    active_social=True,
    contact_data=True,
)


print("\nLEAD INTELLIGENCE\n")

print("Designer:", result.designer_name)
print("Studio:", result.studio_name)

print(
    "Freshness:",
    result.freshness_status,
)

print(
    "Enrichment Action:",
    result.enrichment_action,
)

print(
    "Lead Score:",
    result.lead_score,
)

print(
    "Rug Opportunity Score:",
    result.rug_opportunity_score,
)

print(
    "Rug Used:",
    result.rug_used,
)

print(
    "Supplier Mentioned:",
    result.supplier_mentioned,
)

print(
    "Multiple Projects:",
    result.multiple_projects,
)

print(
    "Active Social:",
    result.active_social,
)

print(
    "Contact Data:",
    result.contact_data,
)