from abc import ABC, abstractmethod

from tavily import TavilyClient

from app.config.settings import settings


class SearchProvider(ABC):

    @abstractmethod
    def search(
        self,
        query: str,
        max_results: int = 10,
    ) -> list[dict]:
        pass


class TavilySearchProvider(SearchProvider):

    def __init__(self):

        if not settings.tavily_api_key:
            raise ValueError(
                "TAVILY_API_KEY is not configured."
            )

        self.client = TavilyClient(
            api_key=settings.tavily_api_key
        )

    def search(
        self,
        query: str,
        max_results: int = 10,
    ) -> list[dict]:

        print(
            f"[TavilySearch] Searching: {query}"
        )

        response = self.client.search(
            query=query,
            search_depth="basic",
            max_results=max_results,
            include_answer=False,
        )

        results = []

        for item in response.get(
            "results",
            [],
        ):

            results.append(
                {
                    "title": item.get(
                        "title"
                    ),
                    "url": item.get(
                        "url"
                    ),
                    "snippet": item.get(
                        "content"
                    ),
                    "source_type": (
                        "public_web_search"
                    ),
                    "score": item.get(
                        "score"
                    ),
                }
            )

        print(
            f"[TavilySearch] Results: "
            f"{len(results)}"
        )

        return results


class PublicSearchTool:

    def __init__(
        self,
        provider: SearchProvider,
    ):
        self.provider = provider

    def search(
        self,
        query: str,
        max_results: int = 10,
    ) -> list[dict]:

        return self.provider.search(
            query=query,
            max_results=max_results,
        )


class DuckDuckGoSearchProvider(SearchProvider):
    """
    100% Free, zero-API-key web search using DuckDuckGo (via ddgs).
    """

    def search(
        self,
        query: str,
        max_results: int = 10,
    ) -> list[dict]:
        import re
        # Sanitize query: DuckDuckGo breaks on boolean operators and special chars
        clean_query = query.replace("+", " ").replace("*", " ").replace("'", " ").replace('"', " ")
        clean_query = " ".join(clean_query.split())

        print(f"[DuckDuckGoSearch] Searching: {clean_query}")
        try:
            from ddgs import DDGS
        except ImportError:
            try:
                from duckduckgo_search import DDGS
            except ImportError:
                print("[DuckDuckGoSearch] Neither 'ddgs' nor 'duckduckgo_search' installed. Falling back to empty results.")
                return []

        results = []
        try:
            with DDGS() as ddgs:
                raw_results = list(ddgs.text(clean_query, max_results=max_results))
                for item in raw_results:
                    results.append(
                        {
                            "title": item.get("title"),
                            "url": item.get("href") or item.get("url"),
                            "snippet": item.get("body") or item.get("content"),
                            "source_type": "public_web_search",
                            "score": 1.0,
                        }
                    )
        except Exception as exc:
            print(f"[DuckDuckGoSearch] Error during search: {exc}")

        print(f"[DuckDuckGoSearch] Results: {len(results)}")
        return results


class MockSearchProvider(SearchProvider):

    def search(
        self,
        query: str,
        max_results: int = 10,
    ) -> list[dict]:
        return [
            {
                "title": f"Profile - {query}",
                "url": "https://example.com/designer-profile",
                "snippet": f"Design studio portfolio and project records for {query}.",
            }
        ]


def create_search_tool() -> PublicSearchTool:

    provider_name = (
        (settings.search_provider or "").lower().strip()
    )

    if provider_name in ("duckduckgo", "ddg", "ddgs"):
        provider = DuckDuckGoSearchProvider()

    elif provider_name == "tavily":
        if not settings.tavily_api_key:
            provider = MockSearchProvider()
        else:
            provider = TavilySearchProvider()

    elif provider_name in ("mock", "none", ""):
        provider = MockSearchProvider()

    else:

        raise ValueError(
            f"Unsupported search provider: "
            f"{settings.search_provider}"
        )

    return PublicSearchTool(
        provider=provider
    )