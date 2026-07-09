"""Reddit via www.reddit.com/search.json（免费，需桌面 UA）。英文一手讨论=踩坑源。"""
from __future__ import annotations

from lib.common import ROLE_PITFALL, Candidate, http_get_json

WEIGHT = 0.7
SEARCH = "https://www.reddit.com/search.json"


def search(query: str, limit: int = 12) -> list[Candidate]:
    data = http_get_json(SEARCH, {
        "q": query, "sort": "top", "t": "month", "limit": str(limit),
    })
    out = []
    for i, ch in enumerate(data.get("data", {}).get("children", [])):
        d = ch.get("data", {})
        out.append(Candidate(
            source="reddit", title=d.get("title") or "",
            url="https://www.reddit.com" + (d.get("permalink") or ""),
            summary=(d.get("selftext") or "")[:280],
            author=d.get("author") or "", published=str(d.get("created_utc") or ""),
            rank=i, weight=WEIGHT, role=ROLE_PITFALL,
        ))
    return out
