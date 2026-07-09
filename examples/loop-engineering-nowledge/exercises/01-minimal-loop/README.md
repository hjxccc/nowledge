# 练习① · 最小 loop 骨架

> 理论：做中学(Freeman 2014) + 生成效应(Slamecka & Graf 1978)。
> **自己一行行敲出来的和看一遍教程的，是两种记忆。** 别只读，跑一遍再改。

## 跑

```bash
cd exercises/01-minimal-loop
python loop.py
cat MEMORY.md   # 看它把状态写回了磁盘
```

你会看到它自己把 4 件待办**发现→派发→检查→记录→决定**一路做完，全程你没 prompt 一次。
这 40 行就是所有 loop 产品的内核（对照 ROADMAP 慢变量的"五件套"）。

## 先自己想，再动手（合意困难，别跳）

1. ✍️ **不看代码**：如果把 `MEMORY.md` 删了重跑，会发生什么？为什么 loop 敢"每轮从盘里重读"？
2. ✍️ 现在 `check()` 永远返回 True。**改成真会失败的检查**（比如随机失败），观察没过的任务如何回到队尾——这对应五件套的哪一件？
3. ✍️ **升级到并行**：如果两个任务要同时做，代码现在会怎样冲突？这正是 ROADMAP 里 **worktree** 要解决的问题——试着说清它防的是什么。

## 进阶（可选，接真实 agent）

- 把 `mock_agent()` 换成真实 Claude Code / API 调用，让它真的写代码。
- 给 `MEMORY.md` 加"发现"环节：让 agent 自己往待办里加活（对应①定时自动化）。
- 加一个独立的 `reviewer` 函数当子 agent 复核（对应⑤）。

> 做完回到 `checkpoints/01-loop-basics.md` 自测。
