#!/usr/bin/env python3
"""nowledge 发现类查询——"这月/这周 github 前 N hot 项目" + 深色榜单卡片 HTML。

区别于快答/深学（主题类）：这是**发现类**——不搜关键词，按 created 时间窗 + star 排。
现查现答，回答 AI 训练记忆给不了的"最近冒头的热项目"。

用法：
  python discover.py --since month --limit 5 --out hot.html
  python discover.py --since week --lang python --keyword agent --out hot.html --today 2026-07-07
产出：stdout 榜单 + （--out 时）一张深色榜单卡片 HTML。
"""
from __future__ import annotations

import argparse
import datetime as dt
import html
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from lib.sources import github  # noqa: E402

PERIOD_DAYS = {"today": 1, "day": 1, "week": 7, "本周": 7, "month": 30,
               "本月": 30, "这月": 30, "quarter": 90}
TPL = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "templates", "rank-card.html")


def _row_html(rank: int, c: dict) -> str:
    summ = c.get("summary", "")
    stars, desc = "", summ
    if summ.startswith("⭐"):
        head, _, rest = summ.partition(" · ")
        stars, desc = head.replace("⭐", "").strip(), rest
    name = html.escape(c.get("title", ""))
    url = html.escape(c.get("url", ""))
    desc = html.escape(desc.strip() or "（无描述）")
    star_tag = f'<span class="star">★ {html.escape(stars)}</span>' if stars else ""
    return (f'<div class="row"><div class="rank">{rank}</div><div class="body">'
            f'<div class="name"><a href="{url}">{name}</a></div>'
            f'<div class="desc">{desc}</div>'
            f'<div class="meta">{star_tag}</div></div></div>')


def render_card(title: str, asof: str, subtitle: str, foot: str,
                items: list[dict], out: str) -> None:
    with open(TPL, encoding="utf-8") as f:
        tpl = f.read()
    rows = "\n  ".join(_row_html(i + 1, c) for i, c in enumerate(items))
    doc = (tpl.replace("{{TITLE}}", html.escape(title))
              .replace("{{ASOF}}", html.escape(asof))
              .replace("{{SUBTITLE}}", html.escape(subtitle))
              .replace("{{FOOT}}", foot)
              .replace("{{ROWS}}", rows))
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write(doc)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", default="month", help="today/week/month/quarter 或天数")
    ap.add_argument("--limit", type=int, default=5)
    ap.add_argument("--lang", default="", help="按语言过滤，如 python/rust")
    ap.add_argument("--keyword", default="", help="附加主题词，如 agent/llm（留空=全站）")
    ap.add_argument("--out", default="", help="榜单卡片 HTML 落盘路径")
    ap.add_argument("--today", default="", help="覆盖当天 YYYY-MM-DD（测试/复现用）")
    args = ap.parse_args()

    today = dt.date.fromisoformat(args.today) if args.today else dt.date.today()
    days = PERIOD_DAYS.get(args.since) or (int(args.since) if args.since.isdigit() else 30)
    since = (today - dt.timedelta(days=days)).isoformat()

    try:
        cands = github.trending(since, args.limit, args.lang, args.keyword)
    except Exception as e:
        print(f"[fail] github trending 采集失败（可能限流/SSL 瞬断，重试即可）: {e}",
              file=sys.stderr)
        sys.exit(1)
    items = [c.to_dict() for c in cands]

    scope = " · ".join(x for x in [args.keyword, args.lang] if x) or "全站"
    label = {"today": "今日", "week": "本周", "month": "本月"}.get(args.since, f"近{days}天")
    title = f"GitHub {label} Hot Top {len(items)}"
    subtitle = (f"范围：{scope}　筛选：{since} 之后新建 · 按 star 排序　"
                f"（现查 GitHub API，非 AI 训练记忆）")
    foot = ("<b>诚实标注</b>：榜单 = 该时间窗内<b>新建</b>且 star 最高的仓库，"
            "反映'最近冒头'，不含老牌热门；star 数随时在涨，以卡片 as-of 日期为准。")

    print(f"\n🔥 {title}（{scope}，{since} 之后新建，按 star）\n")
    for i, c in enumerate(items):
        print(f"  {i+1}. {c['title']}")
        print(f"     {c['summary'][:90]}")
        print(f"     {c['url']}")
    if not items:
        print("  （空——可能时间窗太窄或语言/关键词过严，放宽再试）")

    if args.out:
        render_card(title, today.isoformat(), subtitle, foot, items, args.out)
        print(f"\n[done] 榜单卡片 → {args.out}", file=sys.stderr)


if __name__ == "__main__":
    main()
