"""GitHub 仓库搜索 via api.github.com（匿名 60 req/h；GITHUB_TOKEN 可提额）。"""
from __future__ import annotations

import os

from lib.common import ROLE_PRACTICE, Candidate, http_get_json

WEIGHT = 0.8
SEARCH = "https://api.github.com/search/repositories"


def _headers() -> dict:
    h = {"Accept": "application/vnd.github+json"}
    tok = os.environ.get("GITHUB_TOKEN")
    if tok:
        h["Authorization"] = f"Bearer {tok}"
    return h


def _to_candidate(r: dict, i: int) -> Candidate:
    return Candidate(
        source="github", title=r.get("full_name") or "",
        url=r.get("html_url") or "",
        summary=f"⭐{r.get('stargazers_count', 0)} · {r.get('description') or ''}"[:280],
        author=(r.get("owner") or {}).get("login", ""),
        published=r.get("pushed_at") or "", rank=i, weight=WEIGHT,
        role=ROLE_PRACTICE,
    )


def search(query: str, limit: int = 10) -> list[Candidate]:
    data = http_get_json(SEARCH, {
        "q": query, "sort": "stars", "order": "desc", "per_page": str(limit),
    }, headers=_headers())
    return [_to_candidate(r, i) for i, r in enumerate(data.get("items", []))]


def trending(since: str, limit: int = 5, language: str = "",
             keyword: str = "", min_stars: int = 10) -> list[Candidate]:
    """发现类：本期新冒头的高 star 仓库。since=起始日 YYYY-MM-DD（本月/本周由上层换算）。
    用 created:>since + sort:stars —— 回答"这月 github 前 N hot 项目"，非关键词搜。"""
    q = f"created:>{since} stars:>{min_stars}"
    if language:
        q += f" language:{language}"
    if keyword:
        q = f"{keyword} {q}"
    data = http_get_json(SEARCH, {
        "q": q, "sort": "stars", "order": "desc", "per_page": str(limit),
    }, headers=_headers())
    return [_to_candidate(r, i) for i, r in enumerate(data.get("items", []))]
