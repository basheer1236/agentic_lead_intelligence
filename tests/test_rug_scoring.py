from app.tools.rug_scoring import calculate_rug_opportunity_score


def main():

    rug = {
        "rug_used": "Yes",
        "handmade": None,
        "custom_made": None,
        "luxury_project": True,
        "multiple_rugs": True,
    }

    score = calculate_rug_opportunity_score(rug)

    print("Rug Opportunity Score:", score)


if __name__ == "__main__":
    main()