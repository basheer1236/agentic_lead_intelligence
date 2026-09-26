from app.tools.ad_search_tool import search_ad


def main():
    import sys
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    results = search_ad("The Comma Collective")

    print("Results:", len(results))

    for result in results[:20]:
        print(result)


if __name__ == "__main__":
    main()