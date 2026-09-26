from app.tools.website_tool import fetch_website


def main():

    website = (
        "https://www.ekaathedesigncollective.com"
    )

    result = fetch_website(
        website
    )

    print("\nWEBSITE:")
    print(result["final_url"])

    print("\nTITLE:")
    print(result["title"])

    print("\nTEXT LENGTH:")
    print(len(result["text"]))

    print("\nEMAILS:")
    print(result["emails"])

    print("\nPHONES:")
    print(result["phones"])

    print("\nSOCIAL:")
    print(result["social"])

    print("\nCONTACT PAGES:")
    for url in result["contact_pages"]:
        print(url)

    print("\nABOUT PAGES:")
    for url in result["about_pages"]:
        print(url)


if __name__ == "__main__":
    main()