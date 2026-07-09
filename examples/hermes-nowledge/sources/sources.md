# 接地料清单 · Hermes Agent（框架原理）

> 第 0 件产出。整理日期 **2026-07-07**。**非 AI 训练记忆**——本主题训练记忆会误答成
> "Hermes = Nous Research 的微调 LLM 系列（Hermes 2/3）"，与本 agent 框架是两码事，故全部现查。
> ⚠️ 这是"官方/社区在说什么"，请先自己基于它建立理解，再看图解。

## 角色三角

| 角色 | 来源 | 为什么选它 |
|---|---|---|
| **原理** | [Hermes Agent 官方文档](https://context7.com/nousresearch/hermes-agent)（via context7）| 一手权威，给出 agent 是什么、跑在哪 |
| **原理** | `agent-loop.md` — Agent Loop Turn Lifecycle（官方 developer-guide）| **框架命脉**：run_conversation() 每轮 9 步生命周期，本图解主依据 |
| **原理** | `agent/conversation_loop.py` — Core Conversation Loop（官方源码）| while 循环真身：max_iterations/budget、interrupt、per-turn checkpoint |
| **原理** | `hermes-agent-self-evolution` 官方文档 | 自我进化子系统：自动优化 skills/工具描述 |
| **实操** | [microsoft/mcp-for-beginners 等社区 repo] | 生态实操（本包聚焦原理，实操留待深入时补）|
| **踩坑/动态** | HN：Migrate from OpenClaw · Nous 官方 "Hermes can now /learn from anything" | 定位与最新能力信号；社区实测口碑仍薄（诚实标注）|

## 引擎自评（诚实标注）
- **踩坑源偏薄**：Hermes 较新，真人长期实测/翻车帖尚少；本包原理充分、"值不值得上手"待补社区角。
- **未逐行核对版本**：官方文档随代码演进，字段名（如 max_iterations）以仓库当前为准。
- 本主题正是 nowledge「快答现查纠旧记忆」的活样本，另见 `../showcase/快答-hermes.md`。
