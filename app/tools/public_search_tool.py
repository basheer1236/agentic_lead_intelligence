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
        settings.search_provider.lower()
    )

    if provider_name == "tavily":
        if not settings.tavily_api_key:
            provider = MockSearchProvider()
        else:
            provider = TavilySearchProvider()

    elif provider_name in ("mock", "none"):
        provider = MockSearchProvider()

    else:

        raise ValueError(
            f"Unsupported search provider: "
            f"{settings.search_provider}"
        )

    return PublicSearchTool(
        provider=provider
    )