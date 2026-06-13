"""Rule-based domain expert agent that answers only from retrieved evidence."""

from __future__ import annotations

import re
from collections import OrderedDict

from autodev_rag.models import ExpertOutput, PlannerOutput, RetrievedChunk


ENTITY_PATTERN = re.compile(
    r"\b(?:REQ-[A-Z]+-\d+|TC-[A-Z]+(?:-[A-Z]+)+-\d+|RISK-[A-Z]+-\d+|BUG-[A-Z]+-\d+|SIG-[A-Z]+-\d+)\b"
)


class DomainExpertAgent:
    def answer(
        self,
        query: str,
        planner_output: PlannerOutput,
        retrieved_chunks: list[RetrievedChunk],
    ) -> ExpertOutput:
        citations = [chunk.citation for chunk in retrieved_chunks]
        related_entities = self._extract_entities(retrieved_chunks)
        evidence_lines = self._summarize_evidence(retrieved_chunks)
        target = planner_output.target_function or "未限定功能"

        answer = "\n".join(
            [
                f"问题类型：{planner_output.intent}",
                f"相关功能：{target}",
                "关键依据：",
                *[f"- {line}" for line in evidence_lines],
                "工程分析：",
                self._analysis_by_intent(planner_output.intent, target, related_entities),
                "建议动作：",
                *self._actions_by_intent(planner_output.intent),
                f"引用依据：{', '.join(citations) if citations else '无'}",
            ]
        )

        return ExpertOutput(
            answer=answer,
            related_entities=related_entities,
            citations=citations,
            assumptions=["基于本项目自构造样例文档和检索片段进行推断，默认不包含真实企业数据。"],
            missing_info=self._missing_info(query, retrieved_chunks),
        )

    def _extract_entities(self, chunks: list[RetrievedChunk]) -> list[str]:
        ordered: OrderedDict[str, None] = OrderedDict()
        for chunk in chunks:
            for entity in ENTITY_PATTERN.findall(chunk.text):
                ordered.setdefault(entity, None)
        return list(ordered.keys())

    def _summarize_evidence(self, chunks: list[RetrievedChunk]) -> list[str]:
        lines: list[str] = []
        for chunk in chunks[:5]:
            preview = " ".join(chunk.text.split())
            if len(preview) > 180:
                preview = f"{preview[:177]}..."
            entity_type = chunk.metadata.get("entity_type", "Unknown")
            function = chunk.metadata.get("function") or "N/A"
            lines.append(f"{chunk.citation} [{entity_type}/{function}] {preview}")
        return lines or ["未检索到可用证据。"]

    def _analysis_by_intent(self, intent: str, target: str, entities: list[str]) -> str:
        entity_text = ", ".join(entities[:12]) if entities else "未识别到显式实体 ID"
        if intent == "requirement_analysis":
            return (
                f"应围绕 {target} 的需求边界、输入信号、降级条件和日志追踪进行核对；"
                f"当前证据中可追踪实体包括 {entity_text}。"
            )
        if intent == "test_case_generation":
            return (
                f"测试补充应从需求条目出发，覆盖 scenario、precondition、steps、expected_result "
                f"和 verified_requirement；当前证据中可追踪实体包括 {entity_text}。"
            )
        if intent == "risk_analysis":
            return (
                f"风险分析应明确 cause、impact、severity 和 mitigation，并把缓解措施连接到测试用例；"
                f"当前证据中可追踪实体包括 {entity_text}。"
            )
        if intent == "defect_diagnosis":
            return (
                f"缺陷诊断应从 symptom 回溯到 related_requirement、相关信号和 suggested_validation；"
                f"当前证据中可追踪实体包括 {entity_text}。"
            )
        return f"可按需求、信号、测试、风险和缺陷维度组织回答；当前证据中可追踪实体包括 {entity_text}。"

    def _actions_by_intent(self, intent: str) -> list[str]:
        if intent == "requirement_analysis":
            return [
                "- 核对需求是否覆盖正常场景、边界条件、异常输入和诊断日志。",
                "- 将需求与信号、测试用例和风险条目建立显式追踪。",
            ]
        if intent == "test_case_generation":
            return [
                "- 优先补齐前置条件、信号注入步骤、期望输出和日志检查点。",
                "- 将每条测试用例绑定到 verified_requirement，避免只验证现象。",
            ]
        if intent == "risk_analysis":
            return [
                "- 将风险原因、影响和缓解措施拆开记录，避免混成单一句子。",
                "- 使用已有测试用例验证 mitigation 是否覆盖目标场景。",
            ]
        if intent == "defect_diagnosis":
            return [
                "- 回放关联测试用例并对齐信号、需求和诊断日志。",
                "- 检查 suspected_root_cause 是否能被现有 evidence 支撑。",
            ]
        return [
            "- 先确认目标功能，再按实体类型补充检索。",
            "- 对无 citation 的结论保持保守表述。",
        ]

    def _missing_info(self, query: str, chunks: list[RetrievedChunk]) -> list[str]:
        joined = "\n".join(chunk.text for chunk in chunks)
        checks = {
            "雨天": ("雨天", "检索结果中缺少雨天场景细节。"),
            "低速": ("低速", "检索结果中缺少低速工况细节。"),
            "高温": ("高温", "检索结果中缺少高温阈值或温升速率细节。"),
            "弯道": ("弯道", "检索结果中缺少弯道曲率或车道线质量细节。"),
        }
        missing = [
            message
            for keyword, (needle, message) in checks.items()
            if keyword in query and needle not in joined
        ]
        if not chunks:
            missing.append("没有检索到 evidence，无法给出可靠工程结论。")
        return missing
