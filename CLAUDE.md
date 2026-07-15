# 项目协作约定

## 工作留痕与进度（Cairn）

- 临时文件：根目录禁止调试脚本、SQL、截图和数据快照；统一放 `.cairn/tasks/MM-DD-<topic>/scratch/`。起任务：`./.cairn/scripts/mktmp.sh <topic>`。
- 任务索引：`.cairn/tasks/INDEX.md` 一行一任务。收尾时在顶部写一句结论并附 2–4 个关键词；跨会话任务标 🚧，并维护任务目录的 `progress.md`。
- 起任务前：先查 `.cairn/tasks/INDEX.md`、`.cairn/sop/目录.md` 和 `.cairn/spec/pitfalls.md`，避免重复探索。
- SOP：可重复操作沉淀到 `.cairn/sop/`；已有 SOP 必须照跑，发现过期当场更新。
- 坑账：踩坑时在 `.cairn/spec/pitfalls.md` 追加日期、问题、对策和关键词；反复或高风险的坑升级为本文件硬规则或 SOP 前置检查。
- 决策：影响未来多个任务的选择记录在 `.cairn/docs/decisions/NNN-<主题>.md`；推翻旧决策时新开记录，并把旧记录标为 superseded。
- Git 分层：`.cairn/tasks/`、任务索引和坑账是个人足迹，默认不提交；`.cairn/sop/`、`.cairn/docs/` 与详细规约是团队资产。
- 禁止独立任务状态指针；状态只存在于任务索引标记与任务自身的 `progress.md`。
