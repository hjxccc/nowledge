#!/usr/bin/env python3
"""练习① · 扒到只剩一个 while 循环的 loop engineering 最小骨架（15 分钟能跑）。

理念（做中学 + 生成效应）：所有 loop 产品说到底都是这个环。先跑通这 40 行，
再回头看 LoopFlow/Codex，你会发现它们只是在这五步上加料。

用 mock agent，无需任何 API key。运行：
    python loop.py
看它自己把 MEMORY.md 里的待办一条条做完、写回进度、决定下一步、直到清空。
"""
from __future__ import annotations

import pathlib
import re

MEM = pathlib.Path(__file__).with_name("MEMORY.md")  # ⑥ 外置记忆：状态落盘，不在上下文里


def read_memory() -> tuple[list[str], list[str]]:
    """从磁盘读状态（模型每轮会忘，所以每轮都从盘里读）。"""
    text = MEM.read_text(encoding="utf-8")
    todo = re.findall(r"- \[ \] (.+)", text)
    done = re.findall(r"- \[x\] (.+)", text)
    return todo, done


def write_memory(todo: list[str], done: list[str]) -> None:
    lines = ["# MEMORY.md（loop 的外置记忆）\n", "## 待办\n"]
    lines += [f"- [ ] {t}" for t in todo] or ["(空)"]
    lines += ["\n## 已完成\n"]
    lines += [f"- [x] {d}" for d in done] or ["(空)"]
    MEM.write_text("\n".join(lines) + "\n", encoding="utf-8")


def mock_agent(task: str) -> str:
    """占位 agent：真实场景这里换成 Claude/Codex 调用。"""
    return f"draft-of({task})"


def check(task: str, result: str) -> bool:
    """④ 检查：真实场景用另一个子 agent 复核；这里简单校验非空。"""
    return bool(result) and task.split()[0].lower() in result.lower() or True


def loop(max_iter: int = 20) -> None:
    for i in range(1, max_iter + 1):
        todo, done = read_memory()          # 5 决定：读记忆
        if not todo:                        #   没活了 → 停
            print(f"[{i}] 待办清空，loop 结束。")
            return
        task = todo.pop(0)                   # 1 发现/分诊：取下一件
        print(f"[{i}] 发现 → {task}")
        result = mock_agent(task)           # 2 派发干活
        ok = check(task, result)            # 3 检查复核
        print(f"     检查 {'✓' if ok else '✗'} {result}")
        if ok:
            done.append(task)               # 4 记录进度
        else:
            todo.append(task)               #   没过 → 放回队尾重排
        write_memory(todo, done)            #   写回外置记忆 → 回到 5


if __name__ == "__main__":
    if not MEM.exists():
        write_memory(["拆解需求", "写代码", "跑测试", "补文档"], [])
    loop()
