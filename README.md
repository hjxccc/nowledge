# Nowledge

> # **AI 答的是旧闻，Nowledge 带你了解最新。**
> **AI answers from a frozen past. Nowledge answers from now.**

![Nowledge — AI 答的是旧闻，Nowledge 带你了解最新](demo/frozen-vs-now.png)

你问 AI 一个新东西，它张口就来——但它的记忆**冻结在训练截止那天**（比如 2026-01），早就过期了，还一脸自信。

**Nowledge 干一件事：现查现答，然后标红「AI 旧记忆在这会答错」。**

```
你：介绍下 Claude Fable 5
🧊 裸 AI：       我训练数据里没有这个模型……（它真的不知道，因为发布在它记忆之后）
⚡ +Nowledge：  Fable 5 = Mythos-class 新模型，2026-06-09 发布，SWE-bench 95%，
               🔴 注意：AI 旧记忆会说"没这模型"——错，现查它已发布并一度被出口管制下架又恢复。
```

装进 Claude Code（或任何支持 Skill 的 agent）。**零 API Key，纯 Python 标准库。**

<details>
<summary>它其实还能做另外三件事（点开）——但你只需记住上面那一件</summary>

| 意图 | 你怎么说 | 它给你什么 |
|---|---|---|
| **发现** | "这月 github 前 5 hot 项目" | 现查榜单 + 一张深色榜单卡片 HTML |
| **深学** | "带我系统学 RAG" | 接地三角源 → 路线图/图解/可跑练习/**间隔复训队列**/讲给 AI 听 |
| **追踪** | "追踪 MCP 最新动态" | 只报上次之后的新增（带日期 delta），可配 Cron |

边界：能一句话答的**静态事实**（哪年发布）不走它、直接搜。
</details>

---

## 别人怎么装（Install）

**前置**：① 一个支持 Skill 的 agent（Claude Code / Cursor / Codex CLI 等，runtime 中立）；② Python 3.8+（脚本**零 pip 依赖**，纯标准库）；③ 联网。

**一键安装（推荐）**：
```bash
# macOS / Linux / Git-Bash
curl -fsSL https://raw.githubusercontent.com/hjxccc/nowledge/main/install.sh | bash

# Windows PowerShell
irm https://raw.githubusercontent.com/hjxccc/nowledge/main/install.ps1 | iex
```
装好后 agent 自动加载 `SKILL.md`，**对它说人话即可**，无需记命令。

**手动装**：`git clone https://github.com/hjxccc/nowledge ~/.claude/skills/nowledge`，
或项目内 `.claude/skills/nowledge/`（仅该项目可用）。

**可选增强**（不装也能用核心）：
- `export GITHUB_TOKEN=xxx` —— 发现模式提高 GitHub 限额（匿名 60 次/时）。
- `web-access` skill + 一个 Chromium 浏览器 —— 只为微信/知乎的 CDP 兜底；核心 T0 源（HN/arXiv/GitHub/context7/掘金）不需要它。

---

## 用法（Usage）

**日常：说人话**——触发词见 `SKILL.md` 的 description。装好后无需碰命令行。

**手动跑引擎**（想直接用判断层时）：
```bash
python scripts/ground.py "RAG 检索增强" --quick        # 快答：秒级出新鲜料
python scripts/ground.py "loop engineering"            # 深学接地：planner 自动选源
python scripts/discover.py --since month --limit 5 --out hot.html   # 发现：本月热榜+卡片
python scripts/track.py "MCP" --dir mcp-track          # 追踪：出 delta digest
python scripts/review.py due --file <主题>-nowledge/progress.json   # 复训：到期回考
python scripts/gate.py <主题>-nowledge                 # 质量 gate：逐件过合格线
```

产物落当前目录 `./<主题>-nowledge/`。

---

## 两条护城河（在组合与形态，不在单件功能）

1. **形态**：多件套一次打包成"本地可动手的学习套件文件夹"——离线、最小、可动手、理论驱动。竞品要么在线站（roadmap.sh）、要么对话辅导、要么单张绘图。
2. **判断层**：面向**学习材料**的、开源可复现的选材引擎（加权 RRF + 实体聚类 MMR + URL 去重 + 角色三角）。aihot 证明"判断比抓取值钱"但它是新闻场景且评分不开源——这块是真空。

> 核心理念：last30days/aihot 把料端给你就结束了，而"读一遍点头 = 流畅性错觉"。**Nowledge 接着逼你把料变成脑子里的东西。**

---

## 结构

```
SKILL.md            主编排（四意图触发词 + 主流程 + 防卸载硬规则 + 失败模式表）
DESIGN.md           设计蓝图（改设计先改这里）
references/         source-registry · judgment-pipeline · learning-science · mayer-checklist
templates/          diagram-dark.html(静态) · diagram-interactive.html(可拖动交互) · ROADMAP.md · checkpoint.md · rank-card.html
scripts/
  ground.py         第0件接地引擎（--quick 快答 / 缺原理自动 context7 兜底）
  discover.py       发现模式（github trending + 榜单卡片）
  track.py          追踪模式（delta digest）
  review.py         间隔复训引擎（1/3/7/16/35 天）
  gate.py           六件套质量 gate（含反 slop 硬验）
  lib/              planner · fusion(RRF) · cluster(MMR) · dedupe · common
  lib/sources/      hackernews · github · arxiv · reddit · juejin · wechat · zhihu · context7 · x(syndication)
examples/
  loop-engineering-nowledge/   完整深学包样板（六件套 + 接地，过 gate）
  hermes-nowledge/             框架原理·深色架构图解样板
  showcase/                    快答/发现/追踪 三种意图的橱窗样例
```

---

## 现状（2026-07-08）

四种意图（快答/发现/深学/追踪）全通；judgment 层纯 stdlib 零 key、已实测联网跑通（HN/GitHub/arXiv/掘金/公众号/context7/**X**）；快答新增 **WebSearch 为一等新鲜源**（覆盖极新主题）；**X 源经官方 syndication 端点实测跑通**（盯 14 个顶级 AI 账号时间线，走 curl 绕 TLS 指纹反爬 + 30min 缓存）；两支路（software/ai-research）冷启动验证、原理源 context7 自动兜底、公众号 CDP 兜底实测通过；触发词经 4 轮独立盲测；darwin 评审 90.7 分。**零 live-unverified 项。**
