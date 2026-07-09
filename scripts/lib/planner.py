"""按主题选源。解决"arXiv 对实践术语是噪声"——不同主题域配不同源。

用法：模型可显式传 domain/lang/intent（它判断更准）；不传则用启发式兜底。
"""
from __future__ import annotations

import re

# 每个主题域推荐的源（只列免费/已内建；缺的 adapter 会被 ground.py 优雅跳过）
SOURCES_BY_DOMAIN = {
    "ai-research": ["arxiv", "x", "hackernews", "github", "reddit"],   # 学术/研究：带 arXiv
    "ai-tooling":  ["x", "hackernews", "github", "reddit"],             # AI 实践/工具术语：剔 arXiv
    "software":    ["hackernews", "github", "juejin", "zhihu"],    # 通用后端/前端
    "non-tech":    ["websearch", "wechat"],
}

# 研究/学术信号 → 才配 arXiv。含 ML/推理系统术语（这些没有 arXiv 原理源就是缺原理）
_RESEARCH = re.compile(
    r"\b(paper|theory|algorithm|neural|transformer|diffusion|architecture|"
    r"proof|benchmark|dataset|embedding|attention|gradient|"
    r"speculative|decoding|sampling|quantization|quantize|distillation|distill|"
    r"fine-?tun\w*|rlhf|dpo|inference|kv[ -]?cache|mixture of experts|moe|"
    r"scaling law|tokeniz\w*|pretrain\w*|self-?attention|flash ?attention|lora|"
    r"论文|定理|算法|证明|采样|蒸馏|量化|微调|注意力)\b", re.I)
# 实践/工具信号 → AI 主题也剔 arXiv
_TOOLING = re.compile(
    r"\b(engineering|framework|sdk|cli|api|agent|prompt|workflow|deploy|"
    r"pipeline|best practice|how to|tutorial|上手|实战|教程|部署|框架)\b", re.I)
_AI = re.compile(
    r"\b(ai|llm|agent|rag|gpt|claude|prompt|model|langchain|langgraph|"
    r"大模型|智能体|生成式)\b", re.I)
_CJK = re.compile(r"[一-鿿]")


def classify(topic: str) -> str:
    t = topic.lower()
    ai = bool(_AI.search(t))
    if ai and _RESEARCH.search(t) and not _TOOLING.search(t):
        return "ai-research"
    if ai:
        return "ai-tooling"        # AI 但偏实践/工具 → 不带 arXiv
    if _RESEARCH.search(t):
        return "ai-research"
    if _TOOLING.search(t) or re.search(r"[a-z]", t):
        return "software"
    return "non-tech"


def plan(topic: str, *, domain: str = "", lang: str = "",
         intent: str = "", exclude: list[str] | None = None) -> list[str]:
    dom = domain or classify(topic)
    srcs = list(SOURCES_BY_DOMAIN.get(dom, SOURCES_BY_DOMAIN["software"]))

    # 语言：中文主题 → 中文源优先，去掉纯英文讨论源 reddit（对中文学习者价值低且常 403）
    is_zh = lang == "zh" or (lang != "en" and bool(_CJK.search(topic)))
    if is_zh:
        pool = [s for s in srcs if s != "reddit"] + ["juejin", "wechat", "zhihu"]
        order = ["github", "juejin", "wechat", "hackernews", "zhihu", "arxiv"]
        srcs = [s for s in order if s in pool] + [s for s in pool if s not in order]
    else:
        srcs = [s for s in srcs if s not in ("juejin", "wechat", "zhihu")]

    # 意图：广度偏 GitHub 趋势/资讯；深度偏 HN/Reddit/知乎讨论
    if intent == "breadth":
        srcs = [s for s in srcs if s not in ("reddit",)]

    for x in (exclude or []):
        srcs = [s for s in srcs if s != x]

    # 去重保序，最多 4 个（最小主义 + 限流）
    seen, out = set(), []
    for s in srcs:
        if s not in seen:
            seen.add(s)
            out.append(s)
    return out[:4]
