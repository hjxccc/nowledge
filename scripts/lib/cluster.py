"""实体聚类 + MMR 选代表。参考 last30days cluster.py（MIT），自包含重写。

不用 embedding：从标题+摘要抽"有信号词"，按实体重叠聚簇；
每簇用 MMR（Carbonell & Goldstein 1998）在"质量"与"多样性"间平衡选代表。
"""
from __future__ import annotations

import re

# 太常见、不构成主题信号的词
_STOP = set("the a an of to and or in on for with is are be how what why "
            "using use guide tutorial 的 了 是 和 与 怎么 如何 什么 教程 入门".split())
_WORD = re.compile(r"[A-Za-z0-9][A-Za-z0-9.+#-]{1,}|[一-鿿]{2,}")


def entities(text: str) -> set[str]:
    out = set()
    for w in _WORD.findall(text or ""):
        lw = w.lower()
        if lw in _STOP or len(lw) < 2:
            continue
        out.add(lw)
    return out


def _overlap(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def cluster(cands: list, thresh: float = 0.28) -> list[list]:
    """实体重叠 > thresh 归为一簇。返回簇列表（每簇按 final_score 降序）。"""
    for c in cands:
        if not c.entities:
            c.entities = entities(f"{c.title} {c.summary}")
    clusters: list[list] = []
    for c in cands:
        for group in clusters:
            if _overlap(c.entities, group[0].entities) >= thresh:
                group.append(c)
                break
        else:
            clusters.append([c])
    for g in clusters:
        g.sort(key=lambda x: x.final_score, reverse=True)
    return clusters


def mmr_pick(group: list, k: int = 2, lam: float = 0.7) -> list:
    """每簇选 k 个代表：λ·质量 − (1−λ)·与已选最大相似度。"""
    if len(group) <= k:
        return list(group)
    chosen: list = [group[0]]
    rest = group[1:]
    while rest and len(chosen) < k:
        best, best_s = None, -1e9
        for c in rest:
            div = max(_overlap(c.entities, s.entities) for s in chosen)
            s = lam * c.final_score - (1 - lam) * div * 100
            if s > best_s:
                best, best_s = c, s
        chosen.append(best)
        rest.remove(best)
    return chosen
