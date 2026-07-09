"""知乎搜索 via web-access CDP 代理（best-effort）。中文深度问答/专栏=踩坑/原理源。

知乎 API(400)+网页(403)都挡 curl，必须走带登录态的浏览器。依赖 web-access 的 CDP
代理在 localhost:3456 运行（先 `check-deps.mjs` 起代理）。
⚠️ 需浏览器里**已登录知乎**——未登录时知乎搜索页只回"未搜索到相关内容"+登录墙，
本 adapter 抽取到 0 条后返回空，由 ground.py 优雅降级（不报错）。
"""
from __future__ import annotations

import json
import urllib.parse
import urllib.request

from lib.common import ROLE_PITFALL, Candidate

WEIGHT = 0.6
PROXY = "http://localhost:3456"

# 锚点式抽取：不依赖会变的卡片 class，直接找指向 问题/专栏/回答 的有效链接，
# 再就近取摘要/作者。比 class 选择器抗知乎前端改版。
_EXTRACT_JS = r"""
(() => {
  const out = [];
  const seen = new Set();
  document.querySelectorAll('a[href*="zhihu.com/question/"], a[href*="zhihu.com/p/"], a[href*="/answer/"]').forEach(a => {
    let href = (a.href || '').split('#')[0];
    const title = (a.innerText || a.textContent || '').trim();
    if (!href || !title || title.length < 6 || seen.has(href)) return;
    seen.add(href);
    const card = a.closest('.SearchResult-Card, .ContentItem, .List-item, .Card') || a.parentElement;
    const rich = card && card.querySelector('.RichText, .SearchItem-excerpt, .excerpt, .content');
    const auth = card && card.querySelector('.AuthorInfo-name, .UserLink-link, [data-za-detail-view-element_name=User]');
    out.push({
      title,
      url: href,
      summary: (rich ? rich.innerText : '').slice(0, 280),
      author: (auth ? auth.innerText : '').trim(),
    });
  });
  return JSON.stringify(out.slice(0, 20));
})()
"""


def _post(path: str, body: str = "", timeout: int = 25) -> str:
    data = body.encode("utf-8")
    req = urllib.request.Request(PROXY + path, data=data, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", "replace")


def _get(path: str, timeout: int = 10) -> str:
    with urllib.request.urlopen(PROXY + path, timeout=timeout) as r:
        return r.read().decode("utf-8", "replace")


def search(query: str, limit: int = 10) -> list[Candidate]:
    url = "https://www.zhihu.com/search?type=content&q=" + urllib.parse.quote(query)
    tid = ""
    try:
        resp = _post("/new", url)
        try:
            j = json.loads(resp)
            tid = j.get("targetId") or j.get("id") or ""
        except Exception:
            tid = resp.strip()
        if not tid:
            return []
        raw = _post(f"/eval?target={tid}", _EXTRACT_JS)
        # 代理回 {"value": "<JSON 串>"}；剥一层拿到里面的字符串再解析
        payload = raw
        try:
            j = json.loads(raw)
            if isinstance(j, dict) and "value" in j:
                payload = j["value"]
        except Exception:
            pass
        rows = json.loads(payload) if isinstance(payload, str) else payload
        if not isinstance(rows, list):
            rows = []
    except Exception:
        return []
    finally:
        if tid:
            try:
                _get(f"/close?target={tid}")
            except Exception:
                pass

    out = []
    for i, r in enumerate(rows[:limit]):
        out.append(Candidate(
            source="zhihu", title=r.get("title", ""), url=r.get("url", ""),
            summary=r.get("summary", ""), author=r.get("author", ""),
            published="", rank=i, weight=WEIGHT, role=ROLE_PITFALL,
        ))
    return out
