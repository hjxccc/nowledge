# Nowledge 设计蓝图（DESIGN.md）

> **一句话**：输入任意技能主题 → 在本地产出一个"边做边学"的学习包，且每个设计决策都挂在一条被验证过的学习科学定律上。
>
> 本文是 SKILL.md / references / templates / scripts 的唯一事实来源。改设计先改这里。

---

## 0. 定位与两条护城河

nowledge 不是"又一个信息聚合工具"，它站在 last30days / aihot 这类工具**之上**：它们把最新鲜的一手料端给你就结束了——而"读一遍点头 = 流畅性错觉"，正是认知卸载的陷阱。**nowledge 的活是接着往下逼你把料变成脑子里的东西。**

两条护城河（都不在单件功能，在组合与形态）：

1. **形态**：多件套一次性打包成"本地可动手的学习套件文件夹"，离线、最小化、可动手、理论驱动。竞品要么在线网站（roadmap.sh）、要么对话辅导（claude-tutors）、要么单张绘图（baoyu-diagram）。
2. **判断层**：面向**学习材料**的、开源可复现的选材/组合引擎。aihot 证明了"判断比抓取值钱"，但它是**新闻场景**且**评分不开源**——迁移不到学习领域。这块是真空。

---

## 1. 总体架构：第 0 件 + 六件套

```
主题
 │
 ▼
┌─────────── 第0件 · 接地引擎（本设计新增） ───────────┐
│  选源(planner) → 采集(fanout) → 去重(dedupe)          │
│  → 加权排序(RRF) → 聚类选代表(MMR) → 来源/作者限流       │
│  产出 sources/ 料清单：带来源+日期+权威度+角色标签      │
│  ⚠️护栏：先让用户/AI 基于料自己提炼路线，再进六件套      │
└───────────────────────────────────────────────────────┘
 │ 料喂进六件套
 ▼
① 最小 ROADMAP.md（关键20% + 慢/快变量分层）
② 深色 HTML 图解（复杂原理可视化）
③ exercises/（15分钟能跑的最小 MVP）
④ 追问 checkpoint（AI 后置，先自答再看）
⑤ 间隔复训节奏（1/3/7 天回访）
⑥ "你讲给 AI 听"（费曼，AI 扮学生追问）
贯穿：合意困难（别太顺）· 信息缺口驱动（先抛完不成的真实项目）
```

产物落当前目录 `./<主题>-nowledge/`，零 API Key（复用 Claude Code 当引擎）。

---

## 2. 第 0 件 · 接地引擎（重点）

### 2.1 信源注册表（三层，按可靠性 + 权威度）

架构表述抄 aihot（T1/T1.5/T2 分层 + 代码优先），实现抄 last30days（免费 endpoint，MIT）。

| 层 | 源 | 给什么信号 | 接入方式（复用已装） | source_weight |
|---|---|---|---|---|
| **T0 骨干**（免费·无 key·内建） | 官方文档 | 慢变量·权威原理 | context7（已装） | 1.0 |
| | arXiv | 一手论文 | `export.arxiv.org/api/query` | 1.0 |
| | Hacker News | 英文技术共识/争论 | `hn.algolia.com/api/v1` | 0.8 |
| | GitHub | repo/star 趋势/awesome | `api.github.com`（GITHUB_TOKEN 可选提额） | 0.8 |
| | Reddit | 英文一手讨论 | `www.reddit.com/*.json` | 0.7 |
| | WebSearch | 兜底发现 | 内置 | 0.5 |
| **T1 中文**（best-effort·CDP） | 微信公众号搜索 | 中文实操/行业 | web-access CDP（搜狗微信） | 0.7 |
| | 稀土掘金 juejin | 中文实操教程 | web-access CDP | 0.7 |
| | 知乎 | 中文深度问答/专栏 | web-access CDP | 0.6 |
| | 小红书 / B站 | 中文入门/视频 | web-access CDP / youtube-transcript | 0.5 |
| **T2 插件**（可选·思路来源） | aihot | 中文 AI 广度动态 | 公开 API | 降级：不硬依赖 |
| | last30days | 跨平台真人热度 | 第三方 skill | 降级：不硬依赖 |

**权重的意义**（抄 aihot）：同一件事，T0 官方源就是比二手转述分高。权重进 RRF 融合公式。

**分级原则**：一期只**内建 T0 全部 + T1 的公众号/掘金**（用户点名要、web-access 现成）。aihot/last30days 彻底降级为"思路来源"，不再运行时调用——**不把命脉交给会被 DDoS、会限流、评分不开源的第三方**。

### 2.2 判断管线（这是"结合哪几个"的答案）

搬 last30days 的骨架（MIT，注明出处），用**经典 IR 算法**而非 embedding/LLM，贴"能用代码就别用模型"：

```
planner   按(主题域 × 语言偏好 × 广度/深度意图)选 2–4 个源 + 拆子查询
fanout    并发采集候选
dedupe    URL 归一化(剥 tracking/www/old/m) + 同源近重去除
cluster   实体重叠聚类 → 每簇 MMR 选代表(相关性↔多样性平衡)
fusion    加权 RRF(RRF_K=60, Cormack 2009) × source_weight 融合成一条排序
balance   来源/作者限流；保证快答不会被单一来源垄断
```

**"结合哪几个"确定答案 = MMR 多样性 + 角色三角**：光多样不够，要保证每个知识点凑齐三个角色，缺哪补哪：

```
每个知识点 = 原理源×1 (官方文档/arXiv → 是什么、为什么) → 喂图解②
           + 实操源×1 (掘金/官方 quickstart → 15分钟能跑)  → 喂练习③
           + 踩坑源×1 (HN/知乎 → 真实困惑与分歧)          → 喂追问④
```

### 2.3 学习价值评审维度（上层 rubric，尚未进入确定性核心分数）

当前核心分数是可复现的加权 RRF，并由 MMR、来源/作者限流和角色三角做组合约束。下面四项用于 agent/人工复核与后续评测，**目前不应宣称已经由 `ground.py` 自动计入 `final_score`**：

| 维度 | 含义 | 备注 |
|---|---|---|
| 覆盖度 | 覆盖 ROADMAP 哪个模块 | 保证关键 20% 都有料，不重复堆 |
| 难度匹配 | 入门/进阶，对齐当前 checkpoint | 合意困难：略高于现有水平 |
| 权威度 | 一手 > 二手 | = source_weight |
| 时效 | 快变量层要新且标日期 | 慢变量原理老的也行 |

**模型/代码分工**：选源、并发采集、去重、RRF、MMR 和来源/作者限流用确定性代码；覆盖度、难度匹配和推荐理由由 agent/人工复核。未来只有在加入可重复评测后，才把这些维度写进自动分数。

---

## 3. 六件套 × 理论映射

| # | 组件 | 产物 | 理论地基（见 references/learning-science.md） |
|---|---|---|---|
| 1 | 最小 ROADMAP | `ROADMAP.md` | 认知负荷/样例效应(Sweller 1988) · 刻意练习(Ericsson 1993) |
| 2 | 深色 HTML 图解 | `diagrams/*.html` | 双重编码(Paivio) · 多媒体学习(Mayer 原则) |
| 3 | 可跑练习 | `exercises/` | 主动学习(Freeman 2014) · 生成效应(Slamecka & Graf 1978) |
| 4 | 追问 checkpoint | `checkpoints/` | 提取练习/测试效应(Roediger & Karpicke 2006) · 认知卸载(Risko & Gilbert 2016) |
| 5 | 间隔复训 | `REVISIT.md` | 遗忘曲线(Ebbinghaus) · 间隔效应(Cepeda 2006) |
| 6 | 讲给 AI 听 | `checkpoints/teach-*.md` | 费曼/导师效应(Chase 2009) |
| — | 第0件 接地 | `sources/` | 认知卸载防护 · 慢/快变量分层 · 信息缺口(Loewenstein 1994) |

贯穿全局：**合意困难**(Bjork)、**信息缺口驱动**(Zeigarnik 1927)。

---

## 4. 防认知卸载护栏（SKILL.md 里写死，不写死就退化成答案机）

1. 第0件产出的是**原料不是结论**——明确标注"这是社区在说什么，不是答案；请先自己提炼路线"。
2. **学习模式：默认「先看懂」（worked-example 优先，样例效应/专长反转），不劈头考人。** 护栏改为"看在前、回在后"——看懂后**必须至少一次轻提取**（讲给 AI 听/回顾题）+ 间隔复训；只有 opt-in 的模式 B 才"先自答再看答案"。纯被动读到底仍是禁止项。
3. "讲给 AI 听"环节 AI **只追问、指出讲不清处，不代讲**。
4. 快变量一律**联网现查 + 标日期 + 标厂商偏向**，不信 AI 训练记忆。
5. 诚实交代**未核实项**（见 example 的 E 节）。

---

## 5. 目录结构

```
nowledge/                     # skill 本体
├── SKILL.md                  # 主编排（短！渐进披露）
├── DESIGN.md                 # 本文
├── references/
│   ├── learning-science.md   # 11 理论 + 7 原则（自查用）
│   ├── mayer-checklist.md    # 画图逐条过的清单
│   ├── source-registry.md    # 三层信源 + endpoint + 权重
│   └── judgment-pipeline.md  # RRF/MMR/去重/角色三角（含 MIT 出处）
├── templates/
│   ├── diagram-dark.html     # 深色 SVG 图解模板
│   ├── ROADMAP.md            # 慢/快变量分层骨架
│   └── checkpoint.md         # 先自答再看的追问模板
├── scripts/lib/              # 判断层 + 免费 adapter（自包含重写）
│   ├── fusion.py             # 加权 RRF
│   ├── cluster.py            # 实体聚类 + MMR
│   ├── dedupe.py             # URL 归一化去重
│   └── sources/              # hackernews / reddit / github / arxiv
└── examples/
    └── <主题>-nowledge/      # 一个跑好的完整样板
```

产物结构（每学一个主题）：
```
./<主题>-nowledge/
├── sources/          第0件料清单（带来源+日期+角色）
├── ROADMAP.md        ①
├── diagrams/         ②
├── exercises/        ③
├── checkpoints/      ④⑥
└── REVISIT.md        ⑤
```

---

## 6. 出处与许可

- **last30days-skill**（MIT, © 2026 Matt Van Horn）：判断层算法（加权 RRF、实体聚类+MMR、URL 归一化）与免费 endpoint 参考其实现，**自包含重写**而非整段 vendoring（其模块相互耦合），在 `judgment-pipeline.md` 注明。
- **RRF**：Cormack et al. 2009。**MMR**：Carbonell & Goldstein 1998。
- **aihot**（数字生命卡兹克）：信源分层（T1/T1.5/T2）与"能用代码就别用模型"的架构思路来源；评分公式未开源，不复制、仅借鉴表述。

---

## 7. 构建顺序

1. ✅ DESIGN.md（本文）
2. SKILL.md + templates（先能手工跑通六件套）
3. references（source-registry / judgment-pipeline / 精简理论）
4. scripts/lib 判断层 + 免费 adapter（先 HN/GitHub/arXiv/Reddit）
5. 拿一个主题（RAG）跑出第一个 example 验证闭环
6. 用 darwin-skill 打分优化 description 触发词
