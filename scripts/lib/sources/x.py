"""X (Twitter) via twitter-cli 真搜索 + syndication 免登录降级。

优先路径：如果本机存在 Agent-Reach 推荐的 ``twitter-cli``（命令名 ``twitter``），
直接做 Latest 关键词搜索并读取 JSON。命令缺失、未认证、限流或格式变化时，不让接地
流程失败，自动退回下面的 syndication 固定账号方案。

背景（2026-07 实测走过的两条路）：
  ✗ 爬 X 搜索页（CDP 借登录态）——X 检测自动化浏览器直接喂白页，抽 0 条，死路。
  ✓ X 自己的**嵌入组件 syndication 端点**对外开放：
    `syndication.twitter.com/srv/timeline-profile/screen-name/<handle>`
    返回该账号时间线 JSON（藏在 __NEXT_DATA__ 里），HTTP 200、真内容、无需登录。
    这是唯一稳定的公开 X 路径（X 官方 embed 产品，对它开绿灯）。

策略：X 不给关键词搜索，所以不搜——改盯一批**顶级 AI 账号**的近期时间线，
按 query 关键词过滤 + 近 N 天 + 互动量（♥+↻）排序。定位=前沿一手真人观点（踩坑/实操）。
关键词一条没命中（如极新的专有名词账号还没发）就返空，由 WebSearch 补广度。
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone, timedelta

from lib.common import ROLE_PITFALL, Candidate

WEIGHT = 0.75  # 真人一手观点，介于官方(1.0)与泛社区之间
RECENT_DAYS = 180  # 时间线里超过这个天数的旧推不作数（保新鲜）
CACHE_TTL = 1800   # syndication 限流严：账号时间线缓存 30 分钟，稳态零网络请求
_CACHE_DIR = os.path.join(os.path.dirname(__file__), ".xcache")
_BROWSER_UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
               "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")

# 精选 AI 前沿账号：工程/研究/产品三类个人 + 官方组织号。
# ⚠️ 加账号前务必先验 syndication 快照新鲜度（`curl .../screen-name/<h>` 看最新 full_text
# 的 created_at）——该端点每个号只返一份缓存快照，很多号(claudeai/huggingface/MistralAI)
# 快照停在 1~4 年前，过 RECENT_DAYS 过滤后 0 贡献、只白白拖冷抓时间，别凭名气加。
AI_ACCOUNTS = [
    # 个人（研究/工程/产品）
    "swyx", "karpathy", "sama", "GregKamradt", "_philschmid", "jerryjliu0",
    "hwchase17", "simonw", "ID_AA_Carmack", "DrJimFan", "alexalbert__",
    "emollick", "rasbt", "_akhaliq",
    # 官方组织号（2026-07 实测快照新鲜；Claude/Claude Code 官宣走 AnthropicAI）
    "AnthropicAI", "OpenAI", "GoogleDeepMind", "cursor_ai", "ollama", "vercel",
]

_NEXT_DATA_RE = re.compile(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', re.S)


def _cache_path(handle: str) -> str:
    return os.path.join(_CACHE_DIR, handle + ".json")


def _read_cache(handle: str, allow_stale: bool = False):
    """新鲜缓存返 rows；allow_stale=True 时即使过期也返（429 兜底）；无缓存返 None。"""
    p = _cache_path(handle)
    try:
        age = time.time() - os.path.getmtime(p)
        if age > CACHE_TTL and not allow_stale:
            return None
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def _write_cache(handle: str, rows: list[dict]) -> None:
    try:
        os.makedirs(_CACHE_DIR, exist_ok=True)
        with open(_cache_path(handle), "w", encoding="utf-8") as f:
            json.dump(rows, f, ensure_ascii=False)
    except Exception:
        pass


def _reuse_stale(handle: str) -> list[dict]:
    """网络失败时复用旧快照并刷新冷却时间，避免每次查询重新撞限流。"""
    rows = _read_cache(handle, allow_stale=True)
    if rows is not None:
        _write_cache(handle, rows)
        return rows
    _write_cache(handle, [])
    return []


def _fetch_timeline(handle: str) -> list[dict]:
    """拉一个账号时间线，抽 [{text,url,author,fav,rt,created}]。带缓存 + 429 回退旧缓存。"""
    fresh = _read_cache(handle)
    if fresh is not None:
        return fresh

    url = ("https://syndication.twitter.com/srv/timeline-profile/screen-name/"
           + handle + "?showReplies=false")
    # 走 curl 子进程：syndication 用 TLS 指纹(JA3)反爬，会 429 掉 Python stdlib 的
    # urllib（同 URL/同头/同时刻 curl 却 200）。curl 在 Win10+/mac/Linux 均自带。
    try:
        p = subprocess.run(
            ["curl", "-s", "-m", "12", "-A", _BROWSER_UA, url],
            capture_output=True, timeout=15,
        )
        raw = p.stdout.decode("utf-8", "replace")
    except Exception:
        # curl 缺失/网络错 → 有旧缓存就用旧的，否则空
        return _reuse_stale(handle)
    if not raw:
        return _reuse_stale(handle)
    m = _NEXT_DATA_RE.search(raw)
    if not m:
        return _reuse_stale(handle)
    try:
        data = json.loads(m.group(1))
    except Exception:
        return _reuse_stale(handle)

    rows: list[dict] = []
    seen: set[str] = set()

    def walk(o):
        if isinstance(o, dict):
            txt = o.get("full_text")
            tid = o.get("id_str")
            if isinstance(txt, str) and tid and tid not in seen:
                seen.add(tid)
                rows.append({
                    "text": txt, "id": tid, "author": "@" + handle,
                    "fav": o.get("favorite_count", 0) or 0,
                    "rt": o.get("retweet_count", 0) or 0,
                    "created": o.get("created_at", ""),
                })
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)

    walk(data)
    _write_cache(handle, rows)
    return rows


def _parse_dt(created: str):
    # "Wed Mar 22 14:39:03 +0000 2023"
    try:
        return datetime.strptime(created, "%a %b %d %H:%M:%S %z %Y")
    except Exception:
        return None


def _parse_cli_dt(value: str):
    """兼容 twitter-cli 的 ISO 日期和 syndication 的 Twitter 日期。"""
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (TypeError, ValueError):
        return _parse_dt(value)


def _cli_rows(data) -> list[dict]:
    """取 twitter-cli schema envelope 中的推文列表，兼容少量版本差异。"""
    if isinstance(data, list):
        return [row for row in data if isinstance(row, dict)]
    if isinstance(data, dict):
        for key in ("tweets", "items", "results"):
            rows = data.get(key)
            if isinstance(rows, list):
                return [row for row in rows if isinstance(row, dict)]
    return []


def _cli_author(row: dict) -> str:
    author = row.get("author") or row.get("user") or {}
    if isinstance(author, str):
        handle = author
    else:
        handle = (author.get("username") or author.get("screen_name")
                  or author.get("screenName") or author.get("handle") or "")
    handle = handle or row.get("username") or row.get("screen_name") or row.get("screenName") or ""
    handle = str(handle).strip().lstrip("@")
    return "@" + handle if handle else ""


def _twitter_cli_authenticated(command: str) -> bool:
    """快速认证预检，避免未登录 CLI 把降级路径拖到搜索超时。"""
    try:
        completed = subprocess.run(
            [command, "status", "--json"], capture_output=True, text=True,
            encoding="utf-8", errors="replace", timeout=10,
            env={**os.environ, "PYTHONIOENCODING": "utf-8"},
        )
        payload = json.loads(completed.stdout.strip())
    except (OSError, subprocess.TimeoutExpired, TypeError, json.JSONDecodeError):
        return False
    return (completed.returncode == 0 and payload.get("ok") is True
            and payload.get("data", {}).get("authenticated") is True)


def _search_twitter_cli(query: str, limit: int) -> list[Candidate] | None:
    """调用 twitter-cli；不可用/失败返回 None，让调用方降级 syndication。"""
    command = shutil.which("twitter")
    if not command or not _twitter_cli_authenticated(command):
        return None
    try:
        completed = subprocess.run(
            [command, "search", query, "-t", "Latest", "--max", str(limit),
             "--full-text", "--json"],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            timeout=35, env={**os.environ, "PYTHONIOENCODING": "utf-8"},
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if completed.returncode != 0:
        return None
    try:
        payload = json.loads(completed.stdout.strip())
    except (TypeError, json.JSONDecodeError):
        return None
    if not isinstance(payload, dict) or payload.get("ok") is not True:
        return None

    out: list[Candidate] = []
    for row in _cli_rows(payload.get("data")):
        text = (row.get("text") or row.get("full_text") or row.get("fullText") or "")
        text = re.sub(r"\s+", " ", str(text)).strip()
        tweet_id = str(row.get("id") or row.get("id_str") or row.get("rest_id") or "")
        author = _cli_author(row)
        url = str(row.get("url") or row.get("tweetUrl") or row.get("tweet_url") or "")
        if not url and tweet_id and author:
            url = f"https://x.com/{author[1:]}/status/{tweet_id}"
        if not text or not url:
            continue
        created = str(row.get("created_at") or row.get("createdAt") or row.get("created") or "")
        dt = _parse_cli_dt(created)
        out.append(Candidate(
            source="x", title=text[:120], url=url, summary=text[:280], author=author,
            published=dt.strftime("%Y-%m-%d") if dt else "", rank=len(out),
            weight=WEIGHT, role=ROLE_PITFALL,
        ))
        if len(out) >= limit:
            break
    return out or None


def _terms(query: str) -> list[str]:
    # 拆出有意义的检索词（长度>2、去纯符号），中英都留
    toks = re.split(r"[\s,，、/|]+", query.strip())
    return [t for t in toks if len(t) > 2]


def _search_syndication(query: str, limit: int = 10) -> list[Candidate]:
    terms = [t.lower() for t in _terms(query)]
    if not terms:
        return []

    # 并发抓账号时间线（stdlib 线程池，~一次请求的墙钟）
    all_rows: list[dict] = []
    try:
        with ThreadPoolExecutor(max_workers=4) as ex:  # syndication 限流严，温和并发
            for rows in ex.map(_fetch_timeline, AI_ACCOUNTS):
                all_rows.extend(rows)
    except Exception:
        return []

    cutoff = datetime.now(timezone.utc) - timedelta(days=RECENT_DAYS)
    hits: list[tuple[int, dict, datetime]] = []
    for r in all_rows:
        low = r["text"].lower()
        if not any(t in low for t in terms):
            continue
        dt = _parse_dt(r["created"])
        if dt is None or dt < cutoff:
            continue
        hits.append((r["fav"] + r["rt"], r, dt))

    # 命中太少就放宽时间窗再来一遍（极新主题账号可能刚发/发得少）
    if len(hits) < 3:
        for r in all_rows:
            low = r["text"].lower()
            if not any(t in low for t in terms):
                continue
            dt = _parse_dt(r["created"])
            if dt is None:
                continue
            if any(h[1]["id"] == r["id"] for h in hits):
                continue
            hits.append((r["fav"] + r["rt"], r, dt))

    hits.sort(key=lambda x: (-x[0], -x[2].timestamp()))

    out: list[Candidate] = []
    for i, (_score, r, dt) in enumerate(hits[:limit]):
        text = re.sub(r"\s+", " ", r["text"]).strip()
        url = f"https://x.com/{r['author'][1:]}/status/{r['id']}"
        out.append(Candidate(
            source="x", title=text[:120], url=url,
            summary=text[:280], author=r["author"],
            published=dt.strftime("%Y-%m-%d"), rank=i, weight=WEIGHT,
            role=ROLE_PITFALL,
        ))
    return out


def search(query: str, limit: int = 10) -> list[Candidate]:
    """优先真实关键词搜索；twitter-cli 不可用时保持原免登录能力。"""
    return _search_twitter_cli(query, limit) or _search_syndication(query, limit)
