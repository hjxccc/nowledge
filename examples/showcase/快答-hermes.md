# 快答样例 · "我想了解一下 Hermes"

> nowledge **快答模式**样板：新鲜度敏感的技术问题，现查现答、还标出"AI 旧记忆会答错哪"。
> 生成命令：`python scripts/ground.py "Hermes agent" --quick`（context7 官方 + HN 社区，~10s）
> as-of **2026-07-07**

---

## 👤 用户

> 我想了解一下 Hermes

## 🤖 nowledge 快答

**一句话**：Hermes Agent 是 **Nous Research** 出的**开源、终端原生的自主 coding/任务 agent**——跑在你自己服务器上，核心卖点是"**会自我进化的持久记忆 agent**"。

**关键特征**（均来自现查官方源）：
- 🧠 **持久记忆**：跨会话不忘，"做到哪了"落盘续得上
- 🛠️ **自己造 skill**（agent-created skills）+ 可 `/learn` from anything（Nous 官方近期动态）
- 🔁 **自我进化**：内建 evolutionary self-improvement，自动优化自己的 skills / 工具描述
- 💬 多平台消息接入，PyPI 安装
- 🧭 定位：官方专门写了"**从 OpenClaw 迁移**"指南——冲着 OpenClaw 那类 agent runtime 去的

🔴 **快答的价值 = 纠正 AI 旧记忆**：训练截止 2026-01，我脑子里的"Hermes + Nous Research"是**它家那条微调大模型系列**（Hermes 2/3，基于 Llama/Mistral）。直接问模型，很可能被讲成"一个开源 LLM"，**而不是**这个终端自主 agent 框架——两码事。现查才纠得过来。

⚠️ **同名坑**：Meta 的 `Hermes` 是 React Native 的 JS 引擎，跟这个 agent 无关。

📌 **诚实标缺**：本轮料以**官方（原理源）**为主，社区实测口碑还薄——是"它宣称是什么"，不是"用户验证过好用"。

---

## 这个样例展示了什么

| 快答契约 | 本例如何体现 |
|---|---|
| ① 开门见山 3–6 句 | 一句话定性 + 5 条关键特征 |
| ② 标 as-of 日期 + 现查来源 | 2026-07-07 · context7 官方文档 + HN/Nous 动态 |
| ③ **旧记忆冲突显式标红** | 🔴 段：模型会误答成"Hermes 微调 LLM 系列" |
| ④ 诚实标缺 | 📌 段：官方为主、社区口碑薄 |
| ⑤ 升级钩子 | 可转深学包（六件套）或补社区踩坑角 |

**一句话**：别人把 Hermes 讲给你（可能还讲的是旧的那个），nowledge 现查纠错 + 诚实交代边界。
