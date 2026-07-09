"""稀土掘金搜索 via api.juejin.cn/search_api（公开，无 key）。中文实操教程=实操源。"""
from __future__ import annotations

from lib.common import ROLE_PRACTICE, Candidate, http_get_json

WEIGHT = 0.7
API = "https://api.juejin.cn/search_api/v1/search"


def search(query: str, limit: int = 12) -> list[Candidate]:
    data = http_get_json(API, {
        "spider": "0", "query": query, "id_type": "0", "cursor": "0",
        "limit": str(limit), "search_type": "0", "sort_type": "0",
        "aid": "2608", "uuid": "0",
    })
    out = []
    i = 0
    for row in data.get("data", []):
        rm = row.get("result_model") or {}
        art = rm.get("article_info") or {}
        aid = art.get("article_id")
        if not aid or not art.get("title"):
            continue  # 过滤非文章结果（沸点/课程等）
        author = (rm.get("author_user_info") or {}).get("user_name", "")
        out.append(Candidate(
            source="juejin", title=art.get("title") or "",
            url=f"https://juejin.cn/post/{aid}",
            summary=(art.get("brief_content") or "")[:280],
            author=author, published=str(art.get("ctime") or ""),
            rank=i, weight=WEIGHT, role=ROLE_PRACTICE,
        ))
        i += 1
    return out
