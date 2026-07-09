"""加权 RRF 融合排序。参考 last30days fusion.py（MIT），自包含重写。

RRF: Cormack, Clarke & Buettcher 2009。多源排序列表按
  score = Σ  weight / (RRF_K + rank)  融合。
source_weight 让 T0 官方源天然压过 T2 二手转述。
"""
from __future__ import annotations

from collections import defaultdict

RRF_K = 60


def weighted_rrf(per_source: dict[str, list], subquery_weight: float = 1.0) -> list:
    """per_source: {源名: [Candidate 按该源排序]}。写回每条 rrf_score，返回融合后降序列表。"""
    agg: dict[str, object] = {}
    score: dict[str, float] = defaultdict(float)
    for _src, items in per_source.items():
        for rank, c in enumerate(items):
            key = c.url
            agg.setdefault(key, c)
            score[key] += subquery_weight * c.weight / (RRF_K + rank + 1)
    for key, c in agg.items():
        c.rrf_score = score[key]  # type: ignore[attr-defined]
    fused = list(agg.values())
    fused.sort(key=lambda x: x.rrf_score, reverse=True)
    return fused


def per_author_cap(cands: list, cap: int = 2) -> list:
    """同一具名作者最多保留 cap 条，防单人刷屏。假定 cands 已按质量降序。
    作者为空的不参与限流（否则会把整源误压到 cap 条）。"""
    seen: dict[str, int] = defaultdict(int)
    out = []
    for c in cands:
        author = (c.author or "").strip().lower()
        if author:
            if seen[author] >= cap:
                continue
            seen[author] += 1
        out.append(c)
    return out
