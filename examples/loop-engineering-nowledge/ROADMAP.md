# Loop Engineering 最小学习路线图

> 整理日期：2026-07-06（快变量部分有保质期，过期重跑第 0 件刷新）
> 来源：见 `sources/sources.md`（本路线由料自己提炼，非 AI 训练记忆）

## 0. 一个你现在还完不成的真实项目（信息缺口驱动）

> 让 Claude Code / Codex **无人值守跑一夜**，自己找活、干活、自查、把"做完/待做"写进磁盘，
> 早上你只看结果不看过程。现在你还做不到——因为你只会一轮一轮手动 prompt。
> 整条路线就是为了补上"从 prompt 到 loop"这个洞。

---

## 1. 慢变量 · 原理层（几年不大变，放心学）

> 可信度【高】：三源（Addy / LangChain / 提出者原话）交叉一致，且**与具体工具解耦**。

只留关键 20%：

1. **一句话本质** — loop engineering = **不再自己 prompt，而是设计一个替你 prompt 的系统**。loop = 递归目标：定义目的，AI 迭代到完成。（Addy Osmani）
2. **它在栈里的位置** — prompt < harness（单个 agent 的运行环境） < **loop**（在 harness 之上，带定时器、能派生小助手、能自我投喂）。
3. **五件套 + 一个记忆**（Steinberger 清单，本主题的核心骨架）：
   ①定时自动化(自己发现/分诊) ②worktree(并行不打架) ③skills(写下项目知识) ④插件/连接器(接已有工具) ⑤子 agent(一个出主意一个复核) ＋ **⑥外置记忆**(磁盘上的 md/看板，跨轮次保存"已完成/下一步")。
4. **为什么必须外置记忆** — 模型每轮之间**会忘光**，所以状态必须落磁盘、不能只在上下文里。（长时 agent 的共同底层）
5. **loop 可以叠**（LangChain/Swyx "loopcraft"）：Loop1=agent 调工具循环 → Loop2=验证循环 → 更高层编排。

**为什么稳**：这五件套 + 外置记忆是"任何长时 agent 都依赖的同一个把戏"，换 Codex 还是 Claude Code 形状一样。抓住它，具体产品一个周末就能上手。

---

## 2. 快变量 · 选型层（每月都在变，用时现查）

> ⚠️ **as-of 2026-07，易过期。** 谁支持哪件、叫什么名字随月变。可信度【中】，未逐一回官方核对。

- **Claude Code**：五件套几乎原生齐活（skills / sub-agents / plugins / worktree）。Boris Cherny "我的工作是写 loop"。
- **Codex app**：Steinberger 清单"几乎一一对应"Codex（Addy 原文，未核对官方）。
- **工具/骨架**：LoopFlow（Claude Code 的 loop）、Neuralyzer（Ralph loop 自清上下文）、LangChain `create_agent`/deepagents（叠 loop 的原语）。
- **别背名字**：这层全是快变量，用时现查 + 标日期即可。

---

## 3. 学习主线（每模块挂三角料 + 六件套动作）

| 模块 | 原理源 | 实操源 | 踩坑源 | 产出组件 |
|---|---|---|---|---|
| loop 本质 & 五件套 | Addy Osmani | orange-book | Addy skeptical 段 | 图解② + checkpoint④ |
| 外置记忆为什么必需 | Addy(长时 agent) | Neuralyzer | — | checkpoint④ |
| 叠 loop（agent→验证） | LangChain | LoopFlow | The Register | 练习③ |

---

## 4. 分歧与争议（不替你拍板）

1. **是不是真范式 or buzzword**：提出者派(Steinberger/Boris/Addy 谨慎乐观) vs The Register(还是离不开人、token 成本高、炒词)。→ 自己判断你的场景值不值。
2. **要不要现在就上**：Addy 本人都说 "still early、我很 skeptical"。→ 当趋势看，别全押。

## 5. 未核实项（诚实标注，防认知卸载）

- 五件套与 Codex/Claude Code 的"一一对应"采信 Addy 原文，未逐产品回官方文档核对。
- Reddit 讨论本次 403 未纳入；arXiv 无相关论文（正常，非技术缺失）。
