import csv
from pathlib import Path
from datetime import datetime

LOG_FILE = Path(__file__).resolve().parent.parent / "data" / "search_logs.csv"


def log_search(query):
    # On read-only hosts (e.g. Vercel) logging is skipped instead of failing the search.
    try:
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

        file_exists = LOG_FILE.exists()

        with LOG_FILE.open("a", encoding="utf-8", newline="") as file:
            writer = csv.writer(file)

            if not file_exists:
                writer.writerow(["query", "timestamp"])

            writer.writerow([
                query,
                datetime.now().isoformat(timespec="seconds")
            ])
    except OSError:
        pass


def get_search_stats():
    if not LOG_FILE.exists():
        return {
            "total_searches": 0,
            "top_queries": [],
            "recent_searches": []
        }

    with LOG_FILE.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        searches = list(reader)

    query_counts = {}

    for search in searches:
        query = search["query"]
        query_counts[query] = query_counts.get(query, 0) + 1

    top_queries = sorted(
        query_counts.items(),
        key=lambda item: item[1],
        reverse=True
    )

    return {
        "total_searches": len(searches),
        "top_queries": [
            {"query": query, "count": count}
            for query, count in top_queries[:5]
        ],
        "recent_searches": searches[-10:][::-1]
    }