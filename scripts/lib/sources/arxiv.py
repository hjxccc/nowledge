"""arXiv via export.arxiv.org/api/query（Atom XML，免费无 key）。一手论文=原理源。"""
from __future__ import annotations

import xml.etree.ElementTree as ET

from lib.common import ROLE_PRINCIPLE, Candidate, http_get

WEIGHT = 1.0
API = "https://export.arxiv.org/api/query"
NS = {"a": "http://www.w3.org/2005/Atom"}


def search(query: str, limit: int = 8) -> list[Candidate]:
    # 原理源是慢变量：相关性 >> 新鲜。按 relevance 排，且多词加引号锁短语，
    # 否则 all:speculative decoding 会把只沾一个词的新论文（水印/量化回归）顶上来。
    q = f'all:"{query}"' if " " in query.strip() else f"all:{query}"
    xml = http_get(API, {
        "search_query": q, "start": "0",
        "max_results": str(limit),
        "sortBy": "relevance", "sortOrder": "descending",
    })
    root = ET.fromstring(xml)
    out = []
    for i, e in enumerate(root.findall("a:entry", NS)):
        title = (e.findtext("a:title", "", NS) or "").strip()
        url = (e.findtext("a:id", "", NS) or "").strip()
        summ = (e.findtext("a:summary", "", NS) or "").strip().replace("\n", " ")
        auth = e.findtext("a:author/a:name", "", NS) or ""
        pub = e.findtext("a:published", "", NS) or ""
        out.append(Candidate(
            source="arxiv", title=title, url=url, summary=summ[:280],
            author=auth, published=pub, rank=i, weight=WEIGHT,
            role=ROLE_PRINCIPLE,
        ))
    return out
