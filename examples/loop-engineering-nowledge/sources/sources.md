# 接地料清单 · loop engineering

> 第 0 件产出。整理日期 2026-07-06，由 `scripts/ground.py` 联网抓取（HN/GitHub/arXiv/Reddit）
> + 交叉核对，**非 AI 训练记忆**（本概念 2026-06 才成型，训练数据里没有）。
> ⚠️ 这是"社区在说什么"，**不是结论**。请先自己基于它提炼路线，再看 ROADMAP。

## 角色三角（每个知识点凑齐三类，缺哪补哪）

| 角色 | 来源 | 日期 | 权威 | 一句话推荐理由（为什么选它，非复述） |
|---|---|---|---|---|
| **原理** | [Addy Osmani · Loop Engineering](https://addyosmani.com/blog/loop-engineering/) | 2026-06-07 | 一等 | **最清楚的定义源**，一句话讲透"loop engineering = 不再自己 prompt，而是设计替你 prompt 的系统"，并给出五件套 |
| **原理** | [LangChain · The Art of Loop Engineering](https://www.langchain.com/blog/the-art-of-loop-engineering) | 2026-06-16 | 一等(有厂商倾向) | 把"loop 是可以叠的"讲清楚：Loop1 Agent→Loop2 验证→…，喂给分层图解 |
| **原理** | Steinberger / Boris Cherny 原话（转引自 Addy） | 2026-06 | 一手引述 | 概念提出者原话，做"为什么"锚点：Boris(Claude Code 负责人)"我不再 prompt，我写 loop" |
| **实操** | [alchaincyf/loop-engineering-orange-book](https://github.com/alchaincyf/loop-engineering-orange-book) | 2026 | 二等(社区) | 中文"橙皮书"，体系化上手材料，喂练习 |
| **实操** | [Show HN: LoopFlow — loop engineering for Claude Code](https://github.com/faisalishfaq2005/loopflow) | 2026-06 | 二等 | 直接是 Claude Code 的 loop 工具，可拆到只剩循环骨架当练习 |
| **实操** | [gintasz/neuralyzer（Ralph loop 自清上下文）](https://github.com/gintasz/neuralyzer) | 2026 | 二等 | 印证"外置记忆/上下文管理"这一件，实操参考 |
| **踩坑/争议** | [The Register · 仍需 human-in-the-loop](https://www.theregister.com/ai-and-ml/2026/06/24/loop-engineering-latest-ai-buzzword-still-needs-humans-in-the-loop/) | 2026-06-24 | 二等(媒体批判) | **泼冷水源**：buzzword、token 成本、仍离不开人，用于"分歧"节，防单一叙事 |
| **踩坑** | Addy 本人 skeptical 段 | 2026-06-07 | 一等 | 定义源自己也说"still early、token 成本可能失控"，诚实边界 |

## 引擎自评（诚实标注）

- **arXiv 8 条全丢弃**：loop engineering 是实践者术语，arXiv 无相关论文，返回的是机器人/音频新论文＝噪声。→ 验证 planner 该按主题选源，这类工具主题不带 arXiv。
- **Reddit 403 被封**：本次降级跳过（需走 CDP/cookies 层，见 web-access）。
- **未核实**：五件套是否在 Codex/Claude Code 里"几乎一一对应"采信 Addy 原文，未逐产品回官方文档核对（属快变量，易变）。
