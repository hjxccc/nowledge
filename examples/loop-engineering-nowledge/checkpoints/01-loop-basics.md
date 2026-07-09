# Checkpoint · loop engineering 基础

> **默认走模式 A（先看懂），别劈头考人。** 有底子/想挑战再翻到模式 B 自测。
> 两种模式最后都汇到「三、你的洞」进复训队列——看在前、回在后，但一定要有"回"。

---
## 模式 A · 先看懂（默认，worked-example 优先）

> nowledge 不替 Addy 讲，它带你读那篇最好的、再补它没给的。

### 一、先读这篇原理源（第0件选中的一手材料）
📖 **先读**：[Addy Osmani · Loop Engineering](https://addyosmani.com/blog/loop-engineering/)（2026-06-07，定义最清楚的一手源）
对照 `diagrams/loop-anatomy.html` 那张图一起看。读懂它，下面是我加的**Addy 没给你的三件增值**。

### 二、nowledge 增值三件（读完再看）
**① 给你的重点与生词**（针对新手）：
- Addy 那句原话是钥匙：*loop engineering = 不再自己 prompt，而是设计一个替你 prompt 的系统*。生词 **loop**≈"发现→派发→检查→记录→决定"这套自动转的环。

**② Addy 没讲、但你会踩的坑**（拉自踩坑源）：
- Addy 自己也承认 still early、**token 成本可能失控**；[The Register](https://www.theregister.com/ai-and-ml/2026/06/24/loop-engineering-latest-ai-buzzword-still-needs-humans-in-the-loop/) 更直接泼冷水：仍**离不开 human-in-the-loop**。别把它当银弹。

**③ 该记住的 3 个点**（不考你，直接给）：
1. **loop ≠ 更会 prompt**：你**设计一个替你 prompt 的系统**、退到环外，从"操作者"变"环的设计者"。（Boris Cherny：我不再 prompt，我写 loop）
2. **外置记忆是命根子**：模型每轮之间会忘光，"做到哪了"必须落磁盘（md/看板）。练习里的 `MEMORY.md` 就是它——去掉它 loop 就失忆、原地打转。
3. **worktree 让并行不打架**：每个并行 agent 一份独立工作副本，否则同时改同一批文件会互相覆盖。

### 三、看完做一次轻量回顾（可跳，但强烈建议）
挑一个最没把握的口头回一下就行：
- 一句话复述 loop engineering 和 prompt engineering 差在哪？
- 如果去掉外置记忆（`MEMORY.md`），loop 会怎样？

---
## 模式 B · 先自答（挑战型，opt-in）

> 合上 ROADMAP 和图解，自己写完再展开答案。

1. loop engineering 和 prompt engineering 的根本区别？ ✍️ ______
2. loop 连续跑一夜、模型每轮会忘，它靠什么记得"做到哪"？去掉会怎样？ ✍️ ______
3. 五件套里的 worktree，为什么并行跑多个 agent 一定需要它？ ✍️ ______

<details><summary>写完点开对照</summary>

1. 你一轮轮握着 agent 打字（你在环里） vs 设计一个替你 prompt 的系统（你退到环外）。（Addy Osmani）
2. 靠外置记忆（磁盘 md/看板）跨轮次存"已完成/下一步"；去掉它模型失忆、loop 无法连续、重复劳动或原地打转。
3. worktree 给每个 agent 独立工作副本，否则并行改同一批文件互相覆盖/冲突。

</details>

---
## 三、你的洞（两种模式都汇到这）
- 没看懂/没答上的点 → `python ../../scripts/review.py add --file progress.json --q "..." --wrong --note "..."`，隔天回考。

## 四、讲给 AI 听（费曼，可选升级）
> 复制给 AI："我把 loop engineering 讲给你听，你扮完全不懂的同事，**只许追问、指出我讲不清处，不许替我讲**。"
> 用大白话讲"五件套 + 外置记忆怎么让 agent 自己转"。讲不顺处 = 还没真懂。
