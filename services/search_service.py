import json
from pathlib import Path

DATA_FILE = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "rules.json"
)


def search_guides(query, k=3):
    query = query.strip().lower()

    if not query:
        return []

    with DATA_FILE.open("r", encoding="utf-8") as file:
        data = json.load(file)

    rules = data.get("rules", [])
    results = []

    for rule in rules:
        searchable_text = " ".join([
            str(rule.get("condition", "")),
            str(rule.get("action", "")),
            " ".join(rule.get("symptom_triggers", []))
            if isinstance(rule.get("symptom_triggers", []), list)
            else str(rule.get("symptom_triggers", ""))
        ]).lower()

        if query in searchable_text:
            results.append(rule)

    return results[:max(0, k)]

