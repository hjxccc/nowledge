#!/usr/bin/env python3
"""nowledge 追踪模式（保持前沿）——第 0 件的轻输出 + delta。

深学模式：料 → 六件套。追踪模式：料 → 带日期的动态摘要，且只给「上次之后的新增」。
配 cron 定时跑，就是你自己的 last30days，但走 nowledge 自己的判断层、不依赖第三方。

用法：
    python track.py "loop engineering"                       # 打印本次新增
    python track.py "loop engineering" --dir loop-track      # 落盘 state.json + digest.md（追加，新在上）
（首跑把当前全部当"新增"；之后每次只报上次之后没见过的条目。）
"""
from __future__ import annotations

import argparse
import json
import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # Windows gbk 控制台兜底
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ground import run  # noqa: E402  复用第 0 件管线（选源→采集→去重→聚类→RRF）
from lib import planner as P  # noqa: E402
from lib.dedupe import normalize_url  # noqa: E402


def load_state(path: str) -> dict:
    if path and os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return {"seen": []}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("topic")
    ap.add_argument("--dir", default="", help="落盘目录（state.json + digest.md）；留空只打印")
    ap.add_argument("--domain", default="")
    ap.add_argument("--lang", default="")
    ap.add_argument("--per-source", type=int, default=10)
    ap.add_argument("--date", default="", help="本次日期标签（YYYY-MM-DD），落盘用")
    args = ap.parse_args()

    sources = P.plan(args.topic, domain=args.domain, lang=args.lang, intent="breadth")
    print(f"[track] {args.topic} · 选源 {sources}", file=sys.stderr)
    items = run(args.topic, sources, args.per_source, reps=2)

    state_path = os.path.join(args.dir, "state.json") if args.dir else ""
    state = load_state(state_path)
    seen = set(state.get("seen", []))

    fresh = [it for it in items if normalize_url(it["url"]) not in seen]
    for it in fresh:
        seen.add(normalize_url(it["url"]))

    if not fresh:
        print("自上次以来没有新动态。")
    else:
        print(f"\n🆕 {args.topic} · 本次新增 {len(fresh)} 条：\n")
        for it in fresh:
            print(f"  [{it['source']}/{it['role']}] {it['title']}")
            print(f"      {it['url']}")

    if args.dir:
        os.makedirs(args.dir, exist_ok=True)
        state["seen"] = sorted(seen)
        with open(state_path, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
        if fresh:
            date = args.date or "(未标日期)"
            lines = [f"\n## {date} · 新增 {len(fresh)} 条\n"]
            for it in fresh:
                lines.append(f"- **[{it['source']}/{it['role']}]** [{it['title']}]({it['url']})")
            digest = os.path.join(args.dir, "digest.md")
            old = ""
            if os.path.exists(digest):
                with open(digest, encoding="utf-8") as f:
                    old = f.read()
            header = f"# {args.topic} · 动态追踪\n" if not old else ""
            body = old.split("\n", 1)[1] if old.startswith("#") else old
            with open(digest, "w", encoding="utf-8") as f:  # 新在上
                f.write((header or f"# {args.topic} · 动态追踪\n") + "\n".join(lines) + "\n" + body)
            print(f"\n[track] 已更新 {digest}（新在上）", file=sys.stderr)


if __name__ == "__main__":
    main()
