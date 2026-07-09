"""URL 归一化去重。参考 last30days fusion._normalize_url（MIT），自包含重写。"""
from __future__ import annotations

import re
import urllib.parse

_TRACKING = re.compile(r"^(utm_|ref$|ref_|fbclid$|gclid$|mc_|spm$|scene$|from$)")
_PREFIX = re.compile(r"^(www\.|old\.|m\.|amp\.)")


def normalize_url(url: str) -> str:
    try:
        p = urllib.parse.urlsplit(url.strip().lower())
    except ValueError:
        return url.strip().lower()
    host = _PREFIX.sub("", p.netloc)
    q = [(k, v) for k, v in urllib.parse.parse_qsl(p.query)
         if not _TRACKING.match(k)]
    q.sort()
    path = p.path.rstrip("/")
    return urllib.parse.urlunsplit(("", host, path, urllib.parse.urlencode(q), ""))


def dedupe(cands: list) -> list:
    """归一化 URL 相同则判重，保 weight 高（并列保靠前）的那条。"""
    best: dict[str, object] = {}
    for c in cands:
        key = normalize_url(c.url)
        cur = best.get(key)
        if cur is None or c.weight > cur.weight:  # type: ignore[attr-defined]
            best[key] = c
    return list(best.values())
