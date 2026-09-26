from bs4 import BeautifulSoup


def parse_article(html: str) -> dict:
    soup = BeautifulSoup(html, "lxml")

    title = soup.title.get_text(strip=True) if soup.title else None

    author_tag = soup.find("meta", attrs={"name": "author"})
    author = author_tag.get("content") if author_tag else None

    description_tag = soup.find("meta", attrs={"name": "description"})
    description = (
        description_tag.get("content")
        if description_tag
        else None
    )

    # Remove elements that aren't useful article content
    for tag in soup([
        "script",
        "style",
        "noscript",
        "nav",
        "footer",
    ]):
        tag.decompose()

    text = soup.get_text(
        separator=" ",
        strip=True,
    )

    links = []

    for link in soup.find_all("a", href=True):
        links.append({
            "text": link.get_text(" ", strip=True),
            "url": link["href"],
        })

    return {
        "title": title,
        "author": author,
        "description": description,
        "text": text,
        "links": links,
    }