import feedparser
from datetime import datetime, timezone


def _parse_date(entry):
    try:
        if entry.get("published_parsed"):
            return datetime(
                *entry.published_parsed[:6],
                tzinfo=timezone.utc
            ).isoformat()
    except Exception:
        pass

    return None


def get_geopolitical_data():
    feeds = [
        (
            "global",
            "https://news.google.com/rss/search?q=geopolitics"
        ),
        (
            "war",
            "https://news.google.com/rss/search?q=war+conflict"
        ),
        (
            "sanctions",
            "https://news.google.com/rss/search?q=sanctions"
        ),
        (
            "energy",
            "https://news.google.com/rss/search?q=oil+geopolitics"
        ),
        (
            "diplomacy",
            "https://news.google.com/rss/search?q=ceasefire+negotiations"
        ),
    ]

    headlines = []
    seen = set()

    for category, url in feeds:
        try:
            feed = feedparser.parse(url)

            for entry in feed.entries[:10]:
                title = str(
                    entry.get("title", "")
                ).strip()

                if not title:
                    continue

                key = title.lower()

                if key in seen:
                    continue

                seen.add(key)

                headlines.append({
                    "category": category,
                    "title": title,
                    "published": _parse_date(entry),
                    "link": entry.get("link"),
                })

        except Exception:
            continue

    return headlines[:50]