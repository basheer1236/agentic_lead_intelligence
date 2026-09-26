from app.agents.rug_scorer import calculate_rug_opportunity_score


test_cases = [
    (
        "No rug",
        {
            "rug_used": "No",
            "handmade": False,
            "custom_made": False,
            "luxury_project": False,
            "multiple_rugs": False,
        },
        0,
    ),
    (
        "Rug mentioned",
        {
            "rug_used": "Yes",
            "handmade": False,
            "custom_made": False,
            "luxury_project": False,
            "multiple_rugs": False,
        },
        30,
    ),
    (
        "Handmade custom rug",
        {
            "rug_used": "Yes",
            "handmade": True,
            "custom_made": True,
            "luxury_project": False,
            "multiple_rugs": False,
        },
        70,
    ),
    (
        "All signals",
        {
            "rug_used": "Yes",
            "handmade": True,
            "custom_made": True,
            "luxury_project": True,
            "multiple_rugs": True,
        },
        100,
    ),
]


for name, rug_data, expected in test_cases:

    score = calculate_rug_opportunity_score(
        rug_data
    )

    print(
        f"{name}: "
        f"score={score}, "
        f"expected={expected}"
    )

    assert score == expected


print("\nAll rug scoring tests passed.")