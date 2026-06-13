# 汽车软件开发流程摘要样例

本文档是自构造的汽车软件开发流程摘要，用于为 AutoDev Multi-Agent RAG 提供过程背景。文中提到 ASPICE、ISO 26262 和 SOTIF 仅作为公开概念背景，不表示本项目完整实现这些标准。

## 需求分析

汽车软件需求分析通常需要将用户功能、系统边界、输入输出信号、异常场景和安全相关约束拆成可追踪条目。对于 AEB、LKA、BMS 等功能，需求不应只描述正常场景，还应覆盖传感器异常、驾驶员接管、降级策略、诊断日志和误触发控制。轻量 schema 可将 Requirement、Function 和 Signal 关联起来，使检索结果更容易解释。

## 测试设计

测试设计需要从需求出发，构造 scenario、precondition、steps 和 expected_result。测试用例应明确 verified_requirement，例如 TC-AEB-RAIN-001 验证 REQ-AEB-003，TC-LKA-CURVE-001 验证 REQ-LKA-003，TC-BMS-HIGH-TEMP-001 验证 REQ-BMS-003。对于 RAG 系统，测试用例不仅是验证材料，也是生成补充测试建议的重要 evidence。

## 风险分析

风险分析关注 cause、impact、severity 和 mitigation。AEB 的雨天误触发、LKA 的边界退出、BMS 的高温告警延迟都可以被建模为 Risk，并追踪到 Function 和 TestCase。该过程借鉴安全工程中对危害、触发条件和缓解措施的关注，但本样例不构成完整安全案例。

## 缺陷闭环

缺陷报告应包含 symptom、related_requirement、suspected_root_cause 和 suggested_validation。缺陷闭环的关键是将 BUG-AEB-001、BUG-LKA-001、BUG-BMS-001 这类问题重新连接到需求、信号、测试和风险分析，而不是只记录现象。RAG 报告应展示 citation，使工程师能快速回到原始样例文档。

## Traceability

Traceability 是本项目的核心展示点。一次问答应保留 Planner 意图识别结果、检索到的 doc_id#chunk_id、Domain Expert 的回答、Verification Agent 的 groundedness_score，以及最终 Markdown 报告和 JSON trace。这样即使默认使用 deterministic local mode，也能展示多智能体协同推理与领域知识工程化的完整闭环。

