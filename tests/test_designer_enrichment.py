from app.tools.designer_profile_tool import (
    fetch_designer_profile,
)

from app.agents.designer_enrichment import (
    DesignerEnrichmentAgent,
)


def main():

    profile_url = (
        "https://www.architecturaldigest.in/"
        "adpro/directory/profile/"
        "ekaa-the-design-collective/"
    )

    profile = fetch_designer_profile(
        profile_url
    )

    agent = DesignerEnrichmentAgent()

    result = agent.enrich(
        designer_name=None,
        studio_name="Ekaa - The Design Collective",
        profile=profile,
    )

    print("\nDESIGNER ENRICHMENT")
    print("===================")

    print(
        result.model_dump_json(
            indent=2
        )
    )


if __name__ == "__main__":
    main()