#!/usr/bin/env python3
"""阻止 Claude 在项目根目录新建临时脚本、调试产物或大数据文件。"""
from __future__ import annotations

import datetime
import json
import os
import re
import sys
from pathlib import Path

HARD_BLOCK_PATTERNS = [
    re.compile(r"^_[^/\\]+\.(py|sql|csv|tsv|json|log|txt|xml|yml|yaml|md|sh)$"),
    re.compile(r"^tmp_[^/\\]+\.(py|sql|csv|tsv|json|log|txt|xml|yml|yaml|md|sh)$"),
    re.compile(r"^(patch|verify|check|fix|find|fetch|probe)_[^/\\]+\.(py|sql)$"),
    re.compile(r"^(trigger|test)[_-][^/\\]+\.(py|sh|png)$"),
    re.compile(r"^(retry|cancelled)_[^/\\]+\.(json|jsonl|py)$"),
]

SIZE_LIMIT_BYTES = 1024 * 1024
LARGE_FILE_EXT = {".json", ".tsv", ".csv", ".log", ".xml", ".txt"}


def recent_tasks(project_root: Path, limit: int = 3) -> list[str]:
    tasks_dir = project_root / ".cairn" / "tasks"
    if not tasks_dir.is_dir():
        return []
    candidates = [
        (p.stat().st_mtime, p.name)
        for p in tasks_dir.iterdir()
        if p.is_dir() and re.match(r"^\d{2}-\d{2}-", p.name)
    ]
    candidates.sort(reverse=True)
    return [name for _, name in candidates[:limit]]


def block_message(name: str, reason: str, project_root: Path) -> str:
    today = datetime.date.today().strftime("%m-%d")
    recent = recent_tasks(project_root)
    options = "\n".join(f"    - .cairn/tasks/{r}/scratch/" for r in recent)
    if not options:
        options = "    （无历史任务，请用 mktmp 起新任务）"
    return (
        f"[block-root-scratch] 阻止写入：{name}\n"
        f"  原因：{reason}\n"
        f"  正确位置：.cairn/tasks/{today}-<topic>/scratch/{name}\n"
        f"  起新任务：./.cairn/scripts/mktmp.sh <topic>\n"
        f"  最近任务：\n{options}"
    )


def main() -> int:
    raw = sys.stdin.read()
    if not raw:
        return 0
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return 0

    tool = payload.get("tool_name") or payload.get("tool", "")
    if tool not in {"Write", "Edit", "MultiEdit"}:
        return 0
    tool_input = payload.get("tool_input") or payload.get("input") or {}
    target = tool_input.get("file_path") or tool_input.get("notebook_path") or ""
    if not target:
        return 0

    try:
        root = Path(os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()).resolve()
        absolute = Path(target).resolve()
        relative = absolute.relative_to(root)
    except (OSError, ValueError):
        return 0

    if tool in {"Edit", "MultiEdit"} and absolute.exists():
        return 0
    if len(relative.parts) != 1:
        return 0

    name = relative.parts[0]
    for pattern in HARD_BLOCK_PATTERNS:
        if pattern.match(name):
            sys.stderr.write(block_message(name, "根目录禁止临时文件", root) + "\n")
            return 2

    content = tool_input.get("content", "")
    if Path(name).suffix.lower() in LARGE_FILE_EXT and isinstance(content, str):
        if len(content.encode("utf-8")) > SIZE_LIMIT_BYTES:
            sys.stderr.write(block_message(name, "根目录禁止超过 1 MB 的数据或日志文件", root) + "\n")
            return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
