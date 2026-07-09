"""Hacker News via hn.algolia.com/api/v1（免费无 key）。

坑（来自 last30days 注释）：points 不在 numericAttributesForFiltering，
放进 numericFilters 会 400。只用 created_at_i 过时间窗。
"""
from __future__ import annotations

import time

from lib.common import ROLE_PITFALL, Candidate, http_get_json

WEIGHT = 0.8
SEARCH = "https://hn.algolia.com/api/v1/search"


def search(query: str, limit: int = 15, days: int = 30) -> list[Candidate]:
    from_ts = int(time.time()) - days * 86400
    data = http_get_json(SEARCH, {
        "query": query,
        "tags": "story",
        "numericFilters": f"created_at_i>{from_ts}",
        "hitsPerPage": str(limit),
    })
    out = []
    for i, h in enumerate(data.get("hits", [])):
        url = h.get("url") or f"https://news.ycombinator.com/item?id={h.get('objectID')}"
        out.append(Candidate(
            source="hackernews", title=h.get("title") or "", url=url,
            summary=(h.get("story_text") or "")[:280],
            author=h.get("author") or "", published=h.get("created_at") or "",
            rank=i, weight=WEIGHT, role=ROLE_PITFALL,
        ))
    return out
