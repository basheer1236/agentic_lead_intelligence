from app.agents.enrichment_gate import (
    decide_enrichment_action,
)


statuses = [
    "NEW",
    "STALE",
    "FRESH",
]


for status in statuses:

    action = decide_enrichment_action(status)

    print(
        f"{status} -> {action}"
    )


print("\nTesting lowercase input:")

print(
    "new ->",
    decide_enrichment_action("new"),
)

print("\nTesting invalid status:")

try:
    decide_enrichment_action("UNKNOWN")
except ValueError as exc:
    print("Error correctly raised:", exc)