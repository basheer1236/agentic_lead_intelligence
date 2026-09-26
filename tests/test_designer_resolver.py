from app.agents.designer_resolver import DesignerResolver


def main():
    resolver = DesignerResolver()

    result = resolver.resolve(
        designer_name="Aayush Golecha and Kushaal Jhaveri",
        studio_name="The Comma Collective",
    )

    print("\nDesigner Resolver Result:")
    print(result)


if __name__ == "__main__":
    main()