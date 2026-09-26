from app.tools.public_search_tool import (
    create_search_tool,
)


def main():
    import sys
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    query = '"Ekaa - The Design Collective" interior design'

    print("\nSEARCH QUERY")
    print("=" * 50)
    print(query)

    search_tool = create_search_tool()

    results = search_tool.search(
        query=query,
        max_results=10,
    )

    print("\nSEARCH RESULTS")
    print("=" * 50)

    for index, result in enumerate(
        results,
        start=1,
    ):

        print(f"\n[{index}]")
        print("TITLE:", result["title"])
        print("URL:", result["url"])
        print("SNIPPET:", result["snippet"])


if __name__ == "__main__":
    main()