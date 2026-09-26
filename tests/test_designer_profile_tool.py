from app.tools.designer_profile_tool import (
    fetch_designer_profile,
)


def main():

    profile_url = (
        "https://www.architecturaldigest.in/"
        "adpro/directory/profile/"
        "ekaa-the-design-collective/"
    )

    result = fetch_designer_profile(
        profile_url
    )

    print("\nPROFILE URL:")
    print(result["profile_url"])

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

    print("\nLINKS:")
    for link in result["links"][:20]:
        print(link)


if __name__ == "__main__":
    main()