"""context7 官方文档 via 公开 HTTP API（keyless，stdlib）——权威原理源。

用途：角色三角缺「原理源」时兜底（尤其 zh-software 主题 arxiv 被剔、无一手论文）。
两步：/api/v1/search 解析主题→库，取信誉最高的库，附一段 llms.txt 摘要。
把"官方文档"当 T0 原理源（weight 1.0），补齐三角的原理格。
"""
from __future__ import annotations

from lib.common import ROLE_PRINCIPLE, Candidate, http_get, http_get_json

WEIGHT = 1.0
SEARCH = "https://context7.com/api/v1/search"
DOCS = "https://context7.com{lib_id}/llms.txt"
FETCH_SNIPPET = True  # 快答模式关掉：省去每条 llms.txt 抓取（描述已够），~快一半


def search(query: str, limit: int = 2) -> list[Candidate]:
    data = http_get_json(SEARCH, {"query": query})
    results = data.get("results", []) if isinstance(data, dict) else []
    # 信誉优先：verified + trustScore 高 + context7 相关性 score 高，取前 limit 个库
    results = [r for r in results if r.get("trustScore", 0) >= 6]
    results.sort(key=lambda r: (r.get("verified", False), r.get("score", 0)), reverse=True)

    out = []
    for i, r in enumerate(results[:limit]):
        lib_id = r.get("id", "")
        if not lib_id:
            continue
        summ = (r.get("description") or "")[:200]
        if FETCH_SNIPPET:
            try:  # 附一小段官方文档正文当摘要，失败也不影响（库条目本身就够当原理源锚）
                snippet = http_get(DOCS.format(lib_id=lib_id),
                                   {"topic": query, "tokens": "400"}, timeout=15)
                first = snippet.strip().splitlines()
                if first:
                    summ = (first[0].lstrip("# ").strip() + " — " + summ)[:220]
            except Exception:
                pass
        out.append(Candidate(
            source="context7", title=f"{r.get('title', lib_id)} · 官方文档",
            url=f"https://context7.com{lib_id}", summary=summ,
            author="", published=r.get("lastUpdateDate", ""),
            rank=i, weight=WEIGHT, role=ROLE_PRINCIPLE,
        ))
    return out
