# 追踪样例 · "保持关注 MCP 最新动态"

> nowledge **追踪模式**样板：走 nowledge 自己的判断层选源/采集/去重，只报**上次之后的新增**（delta），落带日期的 `digest.md`。配 Cron/ScheduleWakeup 每隔几天自动跑 = **你自己的 last30days，但不依赖第三方**。
> 生成命令：`python scripts/track.py "MCP Model Context Protocol" --dir mcp-track --date 2026-07-07`

---

## 两跑见真章（delta 检测）

| 跑第几次 | 输出 | 说明 |
|---|---|---|
| **首跑** | 🆕 新增 15 条 → 写入 `mcp-track/digest.md` + `state.json` | 首次把当前全部当新增 |
| **二跑（立即）** | `自上次以来没有新动态。` | seen-set 去重（URL 归一化）生效，不重复刷屏 |

产物见同目录 `mcp-track/digest.md`（新在上、带日期、带角色标签）。

## 这个样例展示了什么

- **判断层复用**：追踪跑的就是第 0 件那套（planner 选源 → 采集 → RRF/去重），不是另起炉灶。
- **原理源自动兜底也在追踪里生效**：digest 里能看到 `context7/principle` 条目——因为 backfill 下沉进了 `run()`，所有调用方（含 track）一致享有。
- **诚实增量**：只报真·新增，靠 `state.json` 里的 URL 归一化 seen-set，避免"每次都说一堆其实上次见过的"。
- **可定时**：配 Cron 每 N 天自动跑，digest 持续累积（新在上），就是一份**走 nowledge 判断层的个人前沿简报**。

**一句话**：last30days 把料端给你就结束；nowledge 追踪只给你"真·新的那几条"，还能顺手对其中想吃透的起一个深学包。
