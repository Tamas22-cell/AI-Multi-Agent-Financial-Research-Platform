import feedparser
from datetime import datetime, timezone


def _parse_entry_date(entry):
    if hasattr(entry, "published_parsed") and entry.published_parsed:
        try:
            return datetime(
                *entry.published_parsed[:6],
                tzinfo=timezone.utc
            ).isoformat()
        except Exception:
            pass

    if hasattr(entry, "updated_parsed") and entry.updated_parsed:
        try:
            return datetime(
                *entry.updated_parsed[:6],
                tzinfo=timezone.utc
            ).isoformat()
        except Exception:
            pass

    return None


def get_news_data():
    feeds = {
        "markets": (
            "https://news.google.com/rss/search?"
            "q=financial+markets+stocks+bonds"
        ),

        "crypto": (
            "https://news.google.com/rss/search?"
            "q=bitcoin+ethereum+crypto+markets"
        ),

        "macro": (
            "https://news.google.com/rss/search?"
            "q=Fed+inflation+interest+rates+economy"
        ),

        "central_banks": (
            "https://news.google.com/rss/search?"
            "q=Federal+Reserve+ECB+interest+rates"
        ),

        "commodities": (
            "https://news.google.com/rss/search?"
            "q=oil+gold+commodities+markets"
        ),

        "geopolitics": (
            "https://news.google.com/rss/search?"
            "q=war+sanctions+tariffs+geopolitical+markets"
        ),
    }

    headlines = []
    seen_titles = set()

    for category, url in feeds.items():
        try:
            feed = feedparser.parse(url)

            if getattr(feed, "bozo", False):
                continue

            for entry in feed.entries[:10]:
                title = str(
                    getattr(entry, "title", "")
                ).strip()

                if not title:
                    continue

                normalized_title = title.lower()

                if normalized_title in seen_titles:
                    continue

                seen_titles.add(
                    normalized_title
                )

                source_name = None

                if hasattr(entry, "source"):
                    try:
                        source_name = entry.source.get(
                            "title"
                        )
                    except Exception:
                        source_name = None

                headlines.append({
                    "category": category,
                    "title": title,
                    "source": source_name,
                    "published": _parse_entry_date(
                        entry
                    ),
                    "link": getattr(
                        entry,
                        "link",
                        None
                    ),
                })

        except Exception:
            continue

    headlines.sort(
        key=lambda item: (
            item["published"] is not None,
            item["published"] or ""
        ),
        reverse=True
    )

    return headlines[:50]