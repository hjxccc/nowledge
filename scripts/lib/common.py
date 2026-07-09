"""nowledge 判断层公共件：Candidate 数据结构 + stdlib HTTP。

零第三方依赖（只用标准库），可直接被 Claude Code 跑。
算法与结构参考 last30days-skill(MIT, © 2026 Matt Van Horn)，自包含重写。
"""
from __future__ import annotations

import json
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from typing import Any

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 nowledge/0.1")

import re

# 角色三角：每个知识点应凑齐这三类
ROLE_PRINCIPLE = "principle"  # 原理源：官方文档 / arXiv
ROLE_PRACTICE = "practice"    # 实操源：掘金 / quickstart
ROLE_PITFALL = "pitfall"      # 踩坑源：HN / 知乎 / Reddit

# 踩坑信号：掘金/微信实操文里带这些词的，本身就是"避坑/血泪"= 踩坑源。
# 用它把 zh practice 里的踩坑文 retag 成 pitfall，补上 zh 踩坑格（不依赖知乎登录）。
_PITFALL_HINT = re.compile(
    r"踩坑|避坑|填坑|入坑|采坑|翻车|血泪|教训|误区|坑点|陷阱|注意事项|避雷|排雷|"
    r"最佳实践|别再|不要再|常见.{0,4}错误|新手.{0,4}错误|坏习惯|不良实践|排查|复盘|"
    r"事故|问题记录|难在哪|难点|为什么这么难|反模式|gotcha|pitfall|anti-?pattern|"
    r"lessons?[ -]learned|footgun|caveat|common mistakes?|things? i wish", re.I)


def looks_like_pitfall(title: str, summary: str = "") -> bool:
    return bool(_PITFALL_HINT.search(f"{title} {summary}"))


@dataclass
class Candidate:
    source: str                  # 源标识，如 "hackernews"
    title: str
    url: str
    summary: str = ""
    author: str = ""
    published: str = ""          # ISO 日期串，尽量填
    rank: int = 0                # 在本源结果内的名次（0-based），供 RRF 用
    weight: float = 1.0          # source_weight（见 source-registry）
    role: str = ""               # 角色三角标签，可后填
    # 计算字段
    rrf_score: float = 0.0
    final_score: float = 0.0
    reason: str = ""             # 一句话推荐理由（模型填）
    entities: set[str] = field(default_factory=set)

    def to_dict(self) -> dict[str, Any]:
        d = self.__dict__.copy()
        d["entities"] = sorted(self.entities)
        return d


def http_get(url: str, params: dict | None = None, timeout: int = 20,
             headers: dict | None = None) -> str:
    if params:
        url = url + ("&" if "?" in url else "?") + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": UA, **(headers or {})})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", "replace")


def http_get_json(url: str, params: dict | None = None, timeout: int = 20,
                  headers: dict | None = None) -> Any:
    return json.loads(http_get(url, params, timeout, headers))
