#!/usr/bin/env python3
"""nowledge 质量 gate（#1）——产出不靠模型即兴，逐件过合格线。

信条（抄卡兹克 11 版）：能用代码就别用模型。
- 硬验（代码判，确定性）：结构在不在、日期有没有、练习跑不跑得起来……
- 软判（代码判不了）：只输出"⚠ 需复核"提示，交给模型/人，绝不假装通过。

用法：
    python gate.py <主题>-nowledge         # 逐件检查，打印报告
    python gate.py <主题>-nowledge --strict # 有硬伤则 exit 1（可挂 CI/产出后自动跑）
不合格 = 打回对应组件重写，别放行。
"""
from __future__ import annotations

import argparse
import glob
import os
import re
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # Windows gbk 控制台兜底

OK, BAD, WARN = "✅", "❌", "⚠️"


def _read(p: str) -> str:
    try:
        with open(p, encoding="utf-8") as f:
            return f.read()
    except OSError:
        return ""


def check_roadmap(d: str) -> list[tuple]:
    p = os.path.join(d, "ROADMAP.md")
    t = _read(p)
    if not t:
        return [(False, "ROADMAP.md 缺失")]
    r = []
    r.append((("慢变量" in t and "快变量" in t), "慢/快变量分层"))
    r.append((bool(re.search(r"as-of|整理日期|20\d\d-\d\d", t)), "带 as-of 日期"))
    r.append((bool(re.search(r"分歧|争议", t)), "有分歧/争议节（不假装唯一正道）"))
    r.append((bool(re.search(r"未核实|待核|存疑", t)), "诚实标未核实项"))
    r.append((bool(re.search(r"信息缺口|完不成|做不到|真实项目", t)), "有信息缺口项目（制造张力）"))
    # 最小主义：慢变量条目别太多（关键 20%）
    slow = re.findall(r"^\s*\d+[、.\)]", t, re.M)
    r.append((len(slow) <= 12, f"最小主义（编号条目 {len(slow)} ≤ 12）"))
    r.append((None, "关键 20% 是否真关键 / 分层是否准确"))  # 软判
    return r


def check_diagrams(d: str) -> list[tuple]:
    files = glob.glob(os.path.join(d, "diagrams", "*.html"))
    if not files:
        return [(False, "diagrams/*.html 缺失（组件②）")]
    r = []
    for f in files:
        h = _read(f)
        name = os.path.basename(f)
        text_only = re.sub(r"<[^>]+>", "", re.sub(r"<style[\s\S]*?</style>", "", h))
        colors = len(set(re.findall(r"#[0-9a-fA-F]{6}", h)))
        r.append((("<svg" in h), f"{name}: 含 SVG 图（非纯文字墙）"))
        r.append((bool(re.search(r"术语|term|pre-?train", h, re.I)), f"{name}: 有术语速查（预训练）"))
        r.append(("figcaption" in h, f"{name}: 有图注点关系"))
        r.append((colors >= 3, f"{name}: 颜色信号 {colors} 种（≥3 引导视线）"))
        r.append((bool(re.search(r"#0[0-9a-d]|#1[0-6]|background:#0|--bg:#0", h)), f"{name}: 深色主题"))
        r.append((len(text_only) < 4000, f"{name}: 不是文字墙（可见文字 {len(text_only)} < 4000）"))
    return r


def check_exercises(d: str) -> list[tuple]:
    runnables = (glob.glob(os.path.join(d, "exercises", "**", "*.py"), recursive=True)
                 + glob.glob(os.path.join(d, "exercises", "**", "*.js"), recursive=True))
    readmes = glob.glob(os.path.join(d, "exercises", "**", "README*.md"), recursive=True)
    if not runnables:
        return [(False, "exercises 下无可跑脚本（组件③要求 15 分钟能跑）")]
    r = []
    # 杀手锏：练习真能跑起来吗（aihot 式"能用代码就验证"）
    for f in runnables:
        if f.endswith(".py"):
            try:
                cp = subprocess.run([sys.executable, os.path.basename(f)],
                                    cwd=os.path.dirname(f), capture_output=True,
                                    text=True, encoding="utf-8", errors="replace",
                                    timeout=30,
                                    env={**os.environ, "PYTHONIOENCODING": "utf-8"})
                r.append((cp.returncode == 0,
                          f"{os.path.basename(f)} 真能跑通（exit {cp.returncode}）"
                          + (f" · {cp.stderr.strip().splitlines()[-1][:60]}" if cp.returncode else "")))
            except subprocess.TimeoutExpired:
                r.append((False, f"{os.path.basename(f)} 超时（>30s，不算 15 分钟能跑）"))
            except Exception as e:
                r.append((False, f"{os.path.basename(f)} 跑挂：{e}"))
    r.append((bool(readmes), "有 README 引导（含'先自己想'）"))
    if readmes:
        rt = _read(readmes[0])
        r.append((bool(re.search(r"先.*想|先.*答|✍️|不看代码", rt)), "README 有'先自己想'环节"))
    return r


def check_checkpoints(d: str) -> list[tuple]:
    files = glob.glob(os.path.join(d, "checkpoints", "*.md"))
    if not files:
        return [(False, "checkpoints/*.md 缺失（组件④）")]
    r = []
    joined = "\n".join(_read(f) for f in files)
    r.append((bool(re.search(r"先看懂|走查样例|worked|模式\s*A", joined)), "支持'先看懂'模式（默认，不劈头考人）"))
    # 反 slop 硬验：先看懂必须锚定真源（http 外链），否则疑似模型现编讲解替代大V原文
    seg = re.split(r"(?m)^#+.*模式\s*B", joined)[0]  # 切到模式B「标题行」为止，只看先看懂段
    r.append((bool(re.search(r"https?://", seg)),
              "先看懂锚定真源（含 http 外链，非现编讲解替代大V）"))
    r.append((bool(re.search(r"参考答案|answer_ref|answer-ref|对照", joined)), "有参考答案/answer_ref"))
    r.append((bool(re.search(r"洞|复训|review\.py|REVISIT", joined)), "答不上的入复训队列（接⑤）"))
    r.append((bool(re.search(r"讲给\s*AI|费曼|只追问|不代讲", joined)), "有'讲给 AI 听'（⑥，只追问不代讲）"))
    return r


def check_loop(d: str) -> list[tuple]:
    prog = os.path.join(d, "progress.json")
    rev = os.path.join(d, "REVISIT.md")
    r = []
    r.append((os.path.exists(prog), "progress.json 存在（复训队列已通电）"))
    r.append((bool(re.search(r"review\.py|due|grade", _read(rev))), "REVISIT.md 引擎驱动（非手动自觉）"))
    return r


def check_sources(d: str) -> list[tuple]:
    files = glob.glob(os.path.join(d, "sources", "*"))
    if not files:
        return [(False, "sources/ 缺失（第 0 件接地）")]
    t = "\n".join(_read(f) for f in files if f.endswith((".md", ".json")))
    return [
        (bool(re.search(r"不是答案|原料|社区在说", t)), "料清单标注'原料非结论'（护栏）"),
        (bool(re.search(r"原理|实操|踩坑|role", t)), "角色三角标签"),
        (None, "来源是否真一手 / 权威度判断"),
    ]


CHECKS = [
    ("① ROADMAP", check_roadmap),
    ("② 图解", check_diagrams),
    ("③ 练习", check_exercises),
    ("④ checkpoint", check_checkpoints),
    ("⑤⑥ 复训闭环", check_loop),
    ("第0件 接地", check_sources),
]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("dir")
    ap.add_argument("--strict", action="store_true", help="有硬伤则 exit 1")
    args = ap.parse_args()

    hard_fail = 0
    review = 0
    print(f"\n=== nowledge 质量 gate · {args.dir} ===\n")
    for label, fn in CHECKS:
        rows = fn(args.dir)
        bad = [r for r in rows if r[0] is False]
        print(f"{'❌' if bad else '✅'} {label}")
        for ok, desc in rows:
            if ok is None:
                print(f"    {WARN} 需复核：{desc}")
                review += 1
            elif ok:
                print(f"    {OK} {desc}")
            else:
                print(f"    {BAD} {desc}")
                hard_fail += 1
        print()

    print("=" * 40)
    verdict = "不合格 → 打回上面 ❌ 的组件重写" if hard_fail else "硬伤全过，只剩需复核项"
    print(f"硬伤 {hard_fail} 处 · 需复核 {review} 处 → {verdict}")
    if args.strict and hard_fail:
        sys.exit(1)


if __name__ == "__main__":
    main()
