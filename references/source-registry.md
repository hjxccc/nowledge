# 信源注册表（第 0 件用）

三层分级：架构表述抄 aihot（T1/T1.5/T2 + 代码优先），免费实现抄 last30days（MIT）。
**一期只内建：T0 全部 + T1 的公众号/掘金。** aihot/last30days 降级为思路来源，不运行时调用。

## T0 骨干 — 免费·无 key·内建（永远可用，不看第三方脸色）

| 源 | 信号 | 接入 | weight | 备注/坑 |
|---|---|---|---|---|
| 官方文档 | 慢变量·权威原理 | **context7**（已装 MCP） | 1.0 | 优先，一手 |
| arXiv | 一手论文 | `https://export.arxiv.org/api/query?search_query=...` | 1.0 | Atom XML，无需 key |
| Hacker News | 英文技术共识/争论 | `https://hn.algolia.com/api/v1/search`（+`search_by_date`,`items`） | 0.8 | ⚠️ `points>N` 放 numericFilters 会 400；只用 `created_at_i>` 过时间窗 |
| GitHub | repo/star 趋势/awesome | `https://api.github.com/search/repositories`、`/search/issues` | 0.8 | 匿名 60 req/h；`GITHUB_TOKEN` 可选提额到 5000 |
| Reddit | 英文一手讨论 | `https://www.reddit.com/search.json?q=&sort=top&t=month` | 0.7 | 带桌面 UA；子版 `r/<x>/top.json?t=month` |
| **WebSearch** | **前沿广度·极新主题主力** | agent 原生工具 | 0.6 | **快答模式一等新鲜源**：实时、零登录、零反爬对抗，能间接捞 X/HN/reddit 一手讨论。极新主题（新版本号/新模型）平台源滞后时它是主力。实测：搜 "Claude Fable 5" 直接拿到发布日/benchmark/定价/第三方吐槽 |

## T1 中文 — best-effort·走 web-access CDP

| 源 | 信号 | 接入 | weight | 备注 |
|---|---|---|---|---|
| 稀土掘金 juejin | 中文实操教程 | ✅ **已内建** `sources/juejin.py`（`api.juejin.cn/search_api`，公开无 key） | 0.7 | 最稳的中文源，带 digg 数 |
| 微信公众号 | 中文实操/行业 | ✅ **已内建** `sources/wechat.py`（搜狗微信，best-effort） | 0.7 | 反爬时返回空自动降级；正文仍走 web-access CDP（站点经验 `mp.weixin.qq.com.md`）；链接为搜狗跳转链 |
| 知乎 | 中文深度问答/专栏 | ✅ **已内建** `sources/zhihu.py`（web-access CDP，锚点抽取） | 0.6 | API/网页都挡 curl，走带登录态浏览器；**需 Edge 里已登录知乎**，否则返空降级 |
| 小红书 / B站 | 中文入门/视频 | web-access CDP / baoyu-youtube-transcript | 0.5 | 视频取字幕 |
| X (Twitter) | 前沿 AI 一手观点 | ✅ **已内建** `sources/x.py`（可选 twitter-cli 真搜索 + syndication 降级） | 0.75 | 检测到 Agent-Reach 推荐的 `twitter` 命令时，优先 `Latest` 关键词搜索并读 JSON；命令缺失、未认证、限流或格式异常则自动退回 X 官方 syndication 固定账号时间线。真搜索需要 Cookie 且有账号风控，建议专用小号、低频小批量。syndication 免 key 免登录，但快照可能陈旧；用 curl 绕 TLS 指纹限制、缓存 30min。极新主题仍由 WebSearch 补广度。 |

## T2 插件 — 可选·仅思路来源，不硬依赖

| 源 | 为什么不硬接 |
|---|---|
| aihot（`aihot.virxact.com/api/public`） | 卡兹克个人站，会被 DDoS/限流，评分不开源。可当**降级补充**，挂了就跳过 |
| last30days（第三方 skill，需多个 key） | 依赖 keys + 单次数分钟。其算法已被我们自包含重写进 judgment-pipeline |

## 选源规则（planner）

```
选源 = f(主题域 × 语言偏好 × 意图)
  AI/大模型   → context7 + arXiv + HN + GitHub(+aihot 补广度)
  通用后端/前端 → context7 + 掘金 + 知乎 + HN + GitHub
  非技术       → WebSearch + 公众号
  要中文落地   → T1 为主 ;  要一手前沿 → T0 英文(HN/arXiv/Reddit)
  广度(该学啥) → GitHub 趋势 / 公众号 ;  深度(学透一点) → HN / 知乎 / Reddit
每主题选 2–4 源，别全跑（最小主义 + 限流）。
```

新增/验证某源后，把有效 endpoint 和坑回写到本文件与 web-access 站点经验。
