from app.tools.public_source_tool import (
    fetch_public_source,
)


def main():

    url = (
        "https://www.ekaathedesigncollective.com"
    )

    result = fetch_public_source(
        url
    )

    print(
        "\nPUBLIC SOURCE RESULT"
    )

    print("=" * 60)

    print(
        "URL:",
        result["requested_url"],
    )

    print(
        "Final URL:",
        result["final_url"],
    )

    print(
        "Title:",
        result["title"],
    )

    print(
        "Source Type:",
        result["source_type"],
    )

    print(
        "Fetch Method:",
        result["fetch_method"],
    )

    print(
        "Fetch Status:",
        result["fetch_status"],
    )

    print(
        "Text Length:",
        len(result["text"]),
    )

    print(
        "\nEmails:"
    )

    for email in result["emails"]:
        print("-", email)

    print(
        "\nPhones:"
    )

    for phone in result["phones"]:
        print("-", phone)

    print(
        "\nSocial:"
    )

    for platform, urls in result[
        "social"
    ].items():

        print(
            f"{platform}:"
        )

        for social_url in urls:
            print(
                "  -",
                social_url,
            )

    print(
        "\nFirst 1000 characters:"
    )

    print(
        result["text"][:1000]
    )


if __name__ == "__main__":
    main()