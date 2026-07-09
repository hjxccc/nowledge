# Example · "AI Agent 开发" 的检索接地(grounding)产物

> nowledge 组件① 路线图 生成前的"找大纲"步骤实跑样板。执行于 2026-07,由联网检索 + 交叉核对产生,**非模型记忆**。演示"慢/快变量分层 + 带日期来源 + 摊开分歧 + 诚实标注未核实"。

## A. 用到的来源(5 个)

| # | 标题 | 链接 | 日期 | 等级 | 一句话 |
|---|---|---|---|---|---|
| 1 | roadmap.sh — AI Agents Roadmap | roadmap.sh/ai-agents | 活文档"2026 edition" | 二等 | 交互式"设计→构建→上线 agent"学习路径 |
| 2 | Anthropic — Building Effective AI Agents | anthropic.com/research/building-effective-agents | 2024-12,架构版 2026 | **一等** | workflow vs agent;从简做起、少用框架、工具是一等公民 |
| 3 | MCP/A2A 协议收敛 | Anthropic + Linux Foundation AAIF 公告 | 2026-03 | 底层一等 | MCP 管 agent↔工具,A2A 管 agent↔agent,2026 同归 AAIF |
| 4 | LangChain — Best AI agent frameworks 2026 | langchain.com/resources | 2026 | 二等(厂商,有倾向) | LangGraph 做有状态工作流,CrewAI 做快速原型 |
| 5 | Agent 可观测工具对比 | Latitude / MLflow / Braintrust | 2026 | 二等(厂商) | 可观测独立成类;主流 LangSmith/Langfuse/Braintrust |

**已丢弃**:无日期 SEO 聚合站、Medium/DEV 营销号、来源不明的采用率数字。

## B. 慢变量骨架(原理层,几年不大变) —— 可信度【高】

三类来源交集,按学习主线:

1. **LLM 基础** — token/上下文窗口/采样;模型是"会犯错的概率引擎"
2. **提示工程** — 结构化提示、少样本、把复杂任务拆成可验证步骤
3. **工具调用** — agent 的手;定义 schema、解析调用、接外部 API。**agent 与纯聊天的分水岭**
4. **规划与推理** — ReAct、任务分解、反思、循环控制(何时停)
5. **记忆与上下文管理** — 短期/长期记忆、上下文压缩与检索召回
6. **RAG** — 切分/embedding/召回/重排,私有知识接地
7. **多智能体** — 角色分工、编排、agent 间通信交接
8. **评估与可观测** — 全会话 trace、LLM-as-judge、回归测试、成本/延迟。生产必需
9. **部署与治理** — 护栏、人在环审批、权限鉴权、失败兜底

**为什么稳**:Anthropic 官方(一等)反复强调的"workflow vs agent、从简到繁、工具为核心",与 roadmap.sh、课程列表高度一致,且与框架解耦。多源原话:"理解这些基本件后,任何框架一个周末就能学会。"

## C. 快变量选型(as-of 2026-07) —— 可信度【中】

> ⚠️ **易过期,重跑刷新。** 版本号与"谁涨谁衰"随月变化;多条来自厂商自述,已标偏向。

- **Agent 框架**:LangGraph v0.4(2026-04,生产标准,~400 企业)· CrewAI v0.105(2026-03,最快出原型,复杂后常迁 LangGraph)· Claude Agent SDK(Anthropic 原生,驱动 Claude Code)· AutoGen/AG2、Semantic Kernel(.NET)、LlamaIndex(RAG)、Pydantic AI(类型安全)分场景
- **协议**:MCP(agent↔工具,事实标准)+ A2A(agent↔agent,v1.0);2025-12 同归 Linux Foundation AAIF;生产常并用
- **评估/可观测**:LangSmith(闭源)· Langfuse(开源领先,MIT,2026 被 ClickHouse 收购)· Braintrust(eval 优先,CI 门禁);旁支 Arize Phoenix/Galileo/Laminar/Helicone
- **模型**:Claude / OpenAI / Gemini,另 Mistral/Cohere/HF 及本地(llama.cpp/Jan)

## D. 分歧与争议(不替你拍板)

1. **要不要框架**:Anthropic(一等)主张先直接调 API、框架诱导过度复杂;框架厂商/多数教程默认从 LangGraph/CrewAI 起。→ 看你重"可控可调试"还是"上手快"
2. **LangGraph vs CrewAI**:生产/受监管派选 LangGraph 显式状态机;快速原型派选 CrewAI 角色隐喻。可查迁移模式"CrewAI 起步→LangGraph 落地"
3. **学习路径**:roadmap.sh"广度并列"(被批不给优先级)vs 从业者"少教程多上生产"
4. **采用率数字**:乐观源"MCP 97M 下载/78% 生产";严谨源(Stacklok)只认"41% 组织有限或广泛使用",且标前述数字未经审计。→ 当方向性信号,别当精确值

## E. 可信度自评 + 未核实项

- **自评**:B 层【高】(三源交叉一致、与框架无关);C 层【中】(方向可信,多为厂商自述,版本号未回官方 changelog 逐一核对)
- **未核实**:roadmap.sh 交互 SVG 抓不到纯文本,B 层骨架为多源重建而非逐字抄(需 CDP 渲染);框架版本号采信二手对比文;MCP/A2A 采用数字未回官方仪表盘;模型选型未做当月实测对比

---

## 这个 example 对 nowledge 设计的验证

- ✅ 慢/快变量自动分层,可信度天差地别,各自标注
- ✅ 快变量全部带 `as-of` + 来源 + 厂商偏向提示
- ✅ 分歧摊开,不假装唯一正道
- ✅ 诚实交代未核实项(防认知卸载)
- 🔧 待补强:roadmap.sh 等交互式页面需走 CDP 渲染(web-access skill 的 CDP 层),curl 拿不到正文
