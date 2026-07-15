#!/usr/bin/env python3
"""nowledge 第 0 件 · 接地引擎 CLI（免费 T0 层）。

用法：
  python scripts/ground.py "RAG" --sources hackernews,github,arxiv,reddit --out sources/raw.json

管线：fanout(采集) → RRF 融合 → dedupe → cluster+MMR 选代表 → per-author cap。
输出候选料清单（JSON）。学习价值打分/推荐理由由上层模型在此基础上补。
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
import json
import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # Windows gbk 控制台兜底（CJK/emoji 标题）
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lib import cluster as C  # noqa: E402
from lib import dedupe as D  # noqa: E402
from lib import fusion as F  # noqa: E402
from lib import planner as P  # noqa: E402

ADAPTERS = {}
for _name in ("hackernews", "github", "arxiv", "reddit", "juejin", "wechat", "zhihu", "context7", "x"):
    try:
        ADAPTERS[_name] = __import__(f"lib.sources.{_name}", fromlist=["search"])
    except Exception:
        pass  # adapter 未实现/加载失败 → 该源不可用，plan 时被优雅跳过


def _backfill_principle(topic: str, sources: list[str], result: list[dict]) -> list[dict]:
    """缺原理源（zh/tooling 主题 arxiv 被剔常见）→ context7 拉官方文档补齐。
    放在 run() 里 = 所有调用方（main/track/外部 harness）都一致拿到补齐后的三角。"""
    got = {c["role"] for c in result}
    if "principle" in got or "context7" in sources:
        return result
    mod = ADAPTERS.get("context7")
    if not mod:
        return result
    try:
        bf = mod.search(topic, 2)
        if bf:
            print(f"[backfill] 原理缺口 → context7 补 {len(bf)} 条官方文档", file=sys.stderr)
            return [c.to_dict() for c in bf] + result
    except Exception as e:
        print(f"[backfill] context7 兜底失败（降级跳过）: {e}", file=sys.stderr)
    return result


def run(topic: str, sources: list[str], per_source: int, reps: int,
        quick: bool = False, backfill: bool = True) -> list[dict]:
    per_source_lists: dict[str, list] = {}

    def fetch(s: str) -> tuple[str, list | None, Exception | None]:
        mod = ADAPTERS.get(s)
        if not mod:
            return s, None, None
        try:
            return s, mod.search(topic, per_source), None
        except Exception as e:
            return s, None, e

    workers = min(4, max(1, len(sources)))
    with ThreadPoolExecutor(max_workers=workers) as pool:
        for s, hits, error in pool.map(fetch, sources):
            if hits is None and error is None:
                print(f"[skip] 未知源 {s}", file=sys.stderr)
                continue
            if error is not None:
                print(f"[fail] {s} 采集失败（降级跳过）: {error}", file=sys.stderr)
                continue
            per_source_lists[s] = hits
            print(f"[ok] {s}: {len(hits)} 条", file=sys.stderr)

    # 踩坑 retag：实操源里带"避坑/血泪/教训"的文本身就是踩坑源 → 补 zh 踩坑格，不靠知乎登录
    from lib.common import ROLE_PITFALL, looks_like_pitfall  # noqa: E402
    for hits in per_source_lists.values():
        for c in hits:
            if c.role == "practice" and looks_like_pitfall(c.title, c.summary):
                c.role = ROLE_PITFALL

    fused = F.weighted_rrf(per_source_lists)
    for c in fused:
        c.final_score = c.rrf_score
    fused = D.dedupe(fused)

    if quick:  # 快答：省掉聚类/MMR，dedupe→RRF 直接取前几条，尽量快
        fused.sort(key=lambda x: x.final_score, reverse=True)
        active_sources = sum(bool(items) for items in per_source_lists.values())
        if active_sources >= 2:
            cap = max(1, (reps + active_sources - 1) // active_sources)
            fused = F.per_source_cap(fused, cap=cap)
        result = [c.to_dict() for c in F.per_author_cap(fused, cap=2)[:reps]]
    else:
        reps_out = []
        for group in C.cluster(fused):
            reps_out.extend(C.mmr_pick(group, k=reps))
        reps_out.sort(key=lambda x: x.final_score, reverse=True)
        reps_out = F.per_author_cap(reps_out, cap=2)
        result = [c.to_dict() for c in reps_out]

    if backfill:
        result = _backfill_principle(topic, sources, result)
    return result


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("topic")
    ap.add_argument("--sources", default="", help="显式指定源(逗号分隔)；留空则 planner 按主题自动选")
    ap.add_argument("--domain", default="", help="ai-research/ai-tooling/software/non-tech，覆盖自动判断")
    ap.add_argument("--lang", default="", help="zh/en，覆盖语言判断")
    ap.add_argument("--intent", default="", help="breadth/depth")
    ap.add_argument("--exclude", default="", help="强制排除的源(逗号分隔)")
    ap.add_argument("--per-source", type=int, default=12)
    ap.add_argument("--reps", type=int, default=2, help="每簇选几个代表")
    ap.add_argument("--out", default="")
    ap.add_argument("--no-backfill", action="store_true",
                    help="关掉缺原理源时的 context7 官方文档兜底")
    ap.add_argument("--quick", action="store_true",
                    help="快答模式：只用最快的 2 个源、省聚类、取前几条，尽量快出新鲜料")
    args = ap.parse_args()

    per_source, reps = args.per_source, args.reps
    if args.sources.strip():
        sources = [s.strip() for s in args.sources.split(",") if s.strip()]
    elif args.quick:
        # 快答只挑「快 + 新鲜」的源：context7(官方现状) + HN/掘金(社区脉搏)，2 个封顶
        is_zh = args.lang == "zh" or (args.lang != "en"
                                      and bool(P._CJK.search(args.topic)))
        sources = ["context7", "juejin"] if is_zh else ["context7", "hackernews"]
        per_source, reps = min(per_source, 6), 6
        if ADAPTERS.get("context7"):
            ADAPTERS["context7"].FETCH_SNIPPET = False  # 快答省掉逐条 llms.txt 抓取
        print(f"[quick] 快答选源 {sources}（省聚类+省快照，尽量快）", file=sys.stderr)
    else:
        exclude = [s.strip() for s in args.exclude.split(",") if s.strip()]
        sources = P.plan(args.topic, domain=args.domain, lang=args.lang,
                         intent=args.intent, exclude=exclude)
        print(f"[planner] 主题域={args.domain or P.classify(args.topic)} → 选源 {sources}",
              file=sys.stderr)

    result = run(args.topic, sources, per_source, reps,
                 quick=args.quick, backfill=not args.no_backfill)

    # 角色三角覆盖检查（设计护栏"缺哪补哪/诚实标注缺料"）——run() 已做 context7 兜底，这里只报剩余缺口
    ROLES = {"principle": "原理源(官方/arXiv)", "practice": "实操源(掘金/quickstart)",
             "pitfall": "踩坑源(HN/知乎)"}
    got = {c["role"] for c in result}
    missing = [ROLES[r] for r in ROLES if r not in got]
    if missing:
        print(f"[⚠️ 角色缺口] 只凑到 {sorted(got)}；缺 {missing}。"
              f"→ 踩坑缺→知乎(需登录)/搜狗微信；原理仍缺→手动 --sources 加 context7。"
              f"别把单角色料当全貌，ROADMAP 里如实标'该角色缺料'。", file=sys.stderr)

    blob = json.dumps({"topic": args.topic, "count": len(result),
                       "role_coverage": {"got": sorted(got), "missing": missing},
                       "items": result},
                      ensure_ascii=False, indent=2)
    if args.out:
        os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(blob)
        print(f"[done] {len(result)} 条 → {args.out}", file=sys.stderr)
    else:
        print(blob)


if __name__ == "__main__":
    main()
