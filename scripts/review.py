#!/usr/bin/env python3
"""nowledge 持续学习闭环（组件⑤⑥通电）。

治的就是立项初心——"用 AI 学完爽完就忘"。checkpoint 的"洞"落盘，按间隔调度，
到期把题重新推回来考（只给题、不给答案，强制提取），过了拉长间隔、没过打回重来。

间隔阶梯（对齐 nowledge 的 1/3/7 天设计，Cepeda 2006 间隔效应）：
    [1, 3, 7, 16, 35] 天；答对 → 前进一级；答错 → 归零重来。

无第三方依赖。用法：
    python review.py add   --file <topic>-nowledge/progress.json --q "问题" --answer-ref "checkpoints/x.md#1" [--wrong] [--note "洞"]
    python review.py due   --file <topic>-nowledge/progress.json
    python review.py grade --file <topic>-nowledge/progress.json --id 1 --pass|--fail [--note "..."]
    python review.py stats --file <topic>-nowledge/progress.json
（测试/复现可加 --today YYYY-MM-DD 覆盖当天）
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # Windows gbk 控制台兜底

LADDER = [1, 3, 7, 16, 35]  # 天


def today(args) -> dt.date:
    return dt.date.fromisoformat(args.today) if args.today else dt.date.today()


def load(path: str) -> dict:
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return {"topic": "", "items": []}


def save(path: str, data: dict) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _next_id(items: list) -> int:
    return max((it["id"] for it in items), default=0) + 1


def cmd_add(args) -> None:
    data = load(args.file)
    # 第一次就没答上 → 从阶梯第 0 级(1天)起；答对了 → 也从 1 天起(首轮都要复训一次)
    idx = 0
    due = today(args) + dt.timedelta(days=LADDER[idx])
    item = {
        "id": _next_id(data["items"]), "q": args.q,
        "answer_ref": args.answer_ref or "", "level": idx,
        "due": due.isoformat(), "reps": 0, "lapses": 0 if not args.wrong else 1,
        "note": args.note or "", "history": [],
    }
    data["items"].append(item)
    save(args.file, data)
    print(f"[add] #{item['id']} 已入复训队列，{LADDER[idx]} 天后（{item['due']}）第一次回考。")


def cmd_due(args) -> None:
    data = load(args.file)
    t = today(args)
    due = [it for it in data["items"] if dt.date.fromisoformat(it["due"]) <= t]
    if not due:
        nxt = min((it["due"] for it in data["items"]), default=None)
        print(f"今天没有到期的复训项。{'下一次：' + nxt if nxt else ''}")
        return
    print(f"🔴 到期复训 {len(due)} 题（{data.get('topic','')}）——合上材料，先自己答，再去 answer_ref 对：\n")
    for it in due:
        hole = f"  （上次的洞：{it['note']}）" if it["note"] else ""
        print(f"  #{it['id']}  {it['q']}")
        print(f"       答完对照 → {it['answer_ref']}{hole}")
    print(f"\n答完用：python review.py grade --file {args.file} --id <N> --pass/--fail")


def cmd_grade(args) -> None:
    data = load(args.file)
    it = next((x for x in data["items"] if x["id"] == args.id), None)
    if not it:
        print(f"[err] 找不到 #{args.id}", file=sys.stderr)
        raise SystemExit(1)
    t = today(args)
    passed = bool(args.passed) and not args.failed
    if passed:
        it["reps"] += 1
        it["level"] = min(it["level"] + 1, len(LADDER) - 1)
    else:
        it["lapses"] += 1
        it["level"] = 0  # 打回重来
    if args.note:
        it["note"] = args.note
    it["due"] = (t + dt.timedelta(days=LADDER[it["level"]])).isoformat()
    it["history"].append({"date": t.isoformat(), "result": "pass" if passed else "fail"})
    save(args.file, data)
    msg = "答对，间隔拉长" if passed else "答错，打回从头"
    print(f"[grade] #{it['id']} {msg} → 下次 {LADDER[it['level']]} 天后（{it['due']}）。")


def cmd_stats(args) -> None:
    data = load(args.file)
    items = data["items"]
    t = today(args)
    mastered = [x for x in items if x["level"] >= len(LADDER) - 1]
    due = [x for x in items if dt.date.fromisoformat(x["due"]) <= t]
    print(f"主题：{data.get('topic','')}")
    print(f"  总项 {len(items)} · 今日到期 {len(due)} · 已掌握(顶级) {len(mastered)}")
    for x in items:
        bar = "▰" * (x["level"] + 1) + "▱" * (len(LADDER) - x["level"] - 1)
        print(f"  #{x['id']} [{bar}] due {x['due']} lapses={x['lapses']}  {x['q'][:34]}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["add", "due", "grade", "stats"])
    ap.add_argument("--file", required=True)
    ap.add_argument("--q", default="")
    ap.add_argument("--answer-ref", dest="answer_ref", default="")
    ap.add_argument("--note", default="")
    ap.add_argument("--wrong", action="store_true", help="add 时标记这题当场没答上")
    ap.add_argument("--id", type=int, default=0)
    ap.add_argument("--pass", dest="passed", action="store_true")
    ap.add_argument("--fail", dest="failed", action="store_true")
    ap.add_argument("--today", default="", help="覆盖当天(YYYY-MM-DD)，测试/复现用")
    args = ap.parse_args()
    if args.cmd == "add" and not args.q.strip():
        ap.error("add requires a non-empty --q")
    if args.cmd == "grade":
        if args.id <= 0:
            ap.error("grade requires a positive --id")
        if args.passed == args.failed:
            ap.error("grade requires exactly one of --pass or --fail")
    args.q = args.q.strip()
    {"add": cmd_add, "due": cmd_due, "grade": cmd_grade, "stats": cmd_stats}[args.cmd](args)


if __name__ == "__main__":
    main()
