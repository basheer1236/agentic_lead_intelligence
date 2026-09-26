from app.agents.public_research_agent import (
    PublicResearchAgent,
)

from app.tools.public_search_tool import (
    create_search_tool,
)


def main():
    import sys
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    designer_name = "Mathew Thannimoottil"

    studio_name = (
        "Ekaa - The Design Collective"
    )

    query = (
        '"Ekaa - The Design Collective" '
        'interior design'
    )

    # ---------------------------------------------------------
    # STEP 1: Search the public web
    # ---------------------------------------------------------

    search_tool = create_search_tool()

    search_results = search_tool.search(
        query=query,
        max_results=10,
    )

    print(
        f"\nSearch results received: "
        f"{len(search_results)}"
    )

    # ---------------------------------------------------------
    # STEP 2: Analyze search results
    # ---------------------------------------------------------

    agent = PublicResearchAgent()

    result = agent.research(
        designer_name=designer_name,
        studio_name=studio_name,
        search_results=search_results,
    )

    # ---------------------------------------------------------
    # STEP 3: Display results
    # ---------------------------------------------------------

    print(
        "\nPUBLIC RESEARCH RESULT"
    )

    print("=" * 70)

    print(
        "Designer:",
        result.designer_name,
    )

    print(
        "Studio:",
        result.studio_name,
    )

    print(
        "\nSOURCES"
    )

    print("=" * 70)

    for index, source in enumerate(
        result.sources,
        start=1,
    ):

        print(
            f"\n[{index}]"
        )

        print(
            "Title:",
            source.title,
        )

        print(
            "URL:",
            source.url,
        )

        print(
            "Source Type:",
            source.source_type,
        )

        print(
            "Relevant:",
            source.relevance,
        )

        print(
            "Confidence:",
            source.confidence,
        )

        print(
            "Reason:",
            source.reason,
        )

        print(
            "Evidence:",
            source.evidence,
        )


if __name__ == "__main__":
    main()