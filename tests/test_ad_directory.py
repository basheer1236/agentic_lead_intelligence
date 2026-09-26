from bs4 import BeautifulSoup
from app.tools.ad_directory_tool import fetch_ad_directory


def main():
    html = fetch_ad_directory()
    soup = BeautifulSoup(html, "lxml")

    profile_links = soup.find_all(
        "a",
        href=lambda href: href and "/adpro/directory/profile/" in href,
    )

    print("Total profile links:", len(profile_links))

    print("\nProfiles containing 'comma':")

    for link in profile_links:
        text = link.get_text(" ", strip=True)

        if "comma" in text.lower():
            print({
                "name": text,
                "url": link["href"]
            })


if __name__ == "__main__":
    main()