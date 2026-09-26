from app.agents.lead_scorer import calculate_lead_score


print("No signals:")
print(
    calculate_lead_score()
)


print("\nAD featured + rug:")
print(
    calculate_lead_score(
        featured_in_ad=True,
        rug_mentioned=True,
    )
)


print("\nAll signals:")
print(
    calculate_lead_score(
        featured_in_ad=True,
        luxury_residence=True,
        rug_mentioned=True,
        supplier_mentioned=True,
        multiple_projects=True,
        active_social=True,
        contact_data=True,
    )
)