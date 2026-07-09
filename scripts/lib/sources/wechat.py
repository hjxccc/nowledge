"""微信公众号 via 搜狗微信搜索（best-effort）。中文实操/行业=实操源。

两层取数：
1. curl 层（快、无需浏览器）——搜狗不反爬时直接解析 HTML。
2. CDP 层（兜底）——curl 触发 antispider/返回空时，走 web-access 的浏览器代理
   （localhost:3456，带真实指纹+会话，能过搜狗反爬；同 zhihu.py 架构）。
坑：结果链接是搜狗跳转链(/link?url=)，稳定拿正文仍走 web-access CDP（站点经验 mp.weixin.qq.com.md）。
两层都拿不到 → 返回空，由 ground.py 优雅降级。
"""
from __future__ import annotations

import html as _htmlmod
import json
import re
import urllib.parse
import urllib.request

from lib.common import ROLE_PRACTICE, Candidate, http_get

WEIGHT = 0.7
SEARCH = "https://weixin.sogou.com/weixin"
BASE = "https://weixin.sogou.com"
PROXY = "http://localhost:3456"

_BLOCK = re.compile(r'<div class="txt-box">(.*?)</div>\s*</div>', re.S)
_HREF = re.compile(r'<h3>\s*<a[^>]*href="([^"]+)"[^>]*>(.*?)</a>', re.S)
_SUMM = re.compile(r'<p class="txt-info"[^>]*>(.*?)</p>', re.S)
_ACCT = re.compile(r'class="(?:account|all-time-y2)"[^>]*>(.*?)</(?:a|span)>', re.S)
_ANTI = re.compile(r"antispider|验证码|访问过于频繁|請輸入驗證碼")

# CDP 层：锚点式抽取，找搜狗结果里的标题链接就近取摘要/公众号名，抗前端改版
_EXTRACT_JS = r"""
(() => {
  const out = [];
  const seen = new Set();
  document.querySelectorAll('.news-list li, .news-box li, li[id^="sogou_vr"]').forEach(li => {
    const a = li.querySelector('.txt-box h3 a, h3 a');
    if (!a) return;
    const href = (a.href || '').trim();
    const title = (a.innerText || a.textContent || '').trim();
    if (!href || !title || seen.has(href)) return;
    seen.add(href);
    const p = li.querySelector('.txt-info');
    const ac = li.querySelector('.account, .all-time-y2, .s-p a, .s-p');
    out.push({
      title,
      url: href,
      summary: (p ? p.innerText : '').replace(/\s+/g, ' ').trim().slice(0, 280),
      author: (ac ? ac.innerText : '').trim(),
    });
  });
  return JSON.stringify(out.slice(0, 20));
})()
"""


def _clean(s: str) -> str:
    return _htmlmod.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", s or ""))).strip()


def _proxy_post(path: str, body: str = "", timeout: int = 25) -> str:
    req = urllib.request.Request(PROXY + path, data=body.encode("utf-8"), method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", "replace")


def _proxy_get(path: str, timeout: int = 10) -> str:
    with urllib.request.urlopen(PROXY + path, timeout=timeout) as r:
        return r.read().decode("utf-8", "replace")


def _cdp_search(query: str, limit: int) -> list[Candidate]:
    """curl 被反爬时的兜底：用浏览器（带会话+真实指纹）打开搜狗微信搜索页再抽取。"""
    url = SEARCH + "?" + urllib.parse.urlencode({"type": "2", "query": query, "ie": "utf8"})
    tid = ""
    try:
        resp = _proxy_post("/new", url)
        try:
            j = json.loads(resp)
            tid = j.get("targetId") or j.get("id") or ""
        except Exception:
            tid = resp.strip()
        if not tid:
            return []
        raw = _proxy_post(f"/eval?target={tid}", _EXTRACT_JS)
        payload = raw
        try:  # 代理回 {"value": "<JSON 串>"}，剥一层
            j = json.loads(raw)
            if isinstance(j, dict) and "value" in j:
                payload = j["value"]
        except Exception:
            pass
        rows = json.loads(payload) if isinstance(payload, str) else payload
        if not isinstance(rows, list):
            return []
    except Exception:
        return []  # 代理没起/反爬页仍需人过验证码 → 优雅降级
    finally:
        if tid:
            try:
                _proxy_get(f"/close?target={tid}")
            except Exception:
                pass

    out = []
    for i, r in enumerate(rows[:limit]):
        title = (r.get("title") or "").strip()
        if not title:
            continue
        out.append(Candidate(
            source="wechat", title=title, url=r.get("url", ""),
            summary=(r.get("summary") or "").strip(), author=(r.get("author") or "").strip(),
            published="", rank=i, weight=WEIGHT, role=ROLE_PRACTICE,
        ))
    return out


def _curl_search(query: str, limit: int) -> list[Candidate] | None:
    """curl 层：反爬则返回 None（触发 CDP 兜底），正常则返回结果列表。"""
    page = http_get(SEARCH, {"type": "2", "query": query, "ie": "utf8"})
    if _ANTI.search(page):
        return None
    out = []
    for i, blk in enumerate(_BLOCK.findall(page)[:limit]):
        m = _HREF.search(blk)
        if not m:
            continue
        href, title = m.group(1), _clean(m.group(2))
        if not title:
            continue
        url = href if href.startswith("http") else BASE + href
        sm = _SUMM.search(blk)
        ac = _ACCT.search(blk)
        out.append(Candidate(
            source="wechat", title=title, url=url,
            summary=_clean(sm.group(1)) if sm else "",
            author=_clean(ac.group(1)) if ac else "", published="",
            rank=i, weight=WEIGHT, role=ROLE_PRACTICE,
        ))
    return out


def search(query: str, limit: int = 10) -> list[Candidate]:
    try:
        curl = _curl_search(query, limit)
    except Exception:
        curl = None
    if curl:
        return curl
    # curl 被反爬(None) 或返回空([]) → CDP 兜底
    return _cdp_search(query, limit)
