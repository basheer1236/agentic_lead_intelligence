from app.llm.client import LLMClient


def main():
    llm = LLMClient()

    response = llm.generate(
        "You are a helpful assistant.",
        "Explain an AI agent in one sentence."
    )

    print(response)


if __name__ == "__main__":
    main()