"""Deterministic planner agent."""

from __future__ import annotations

from autodev_rag.models import PlannerOutput


class PlannerAgent:
    INTENT_ENTITIES = {
        "requirement_analysis": ["Requirement", "Function", "Signal"],
        "test_case_generation": ["Requirement", "TestCase", "Signal"],
        "risk_analysis": ["Requirement", "Risk", "TestCase"],
        "defect_diagnosis": ["Defect", "Requirement", "Signal", "TestCase"],
        "general_qa": ["Requirement", "Function", "TestCase", "Risk", "Defect", "Signal"],
    }

    def plan(self, query: str) -> PlannerOutput:
        query_lower = query.lower()
        intent = self._detect_intent(query, query_lower)
        target_function = self._detect_function(query, query_lower)
        needed_entities = self.INTENT_ENTITIES[intent]
        filters: dict[str, object] = {"entity_type": needed_entities}
        if target_function:
            filters["function"] = target_function

        return PlannerOutput(
            intent=intent,
            target_function=target_function,
            needed_entities=needed_entities,
            retrieval_filters=filters,
            reasoning_steps=[
                "Identify target automotive function",
                "Select relevant engineering entity types",
                "Retrieve grounded context from domain documents",
                "Produce structured answer with citations",
                "Verify unsupported claims",
            ],
        )

    def _detect_intent(self, query: str, query_lower: str) -> str:
        test_keywords = ("测试", "test case", "验证", "用例", "test")
        risk_keywords = ("风险", "risk", "危害", "安全")
        defect_keywords = ("缺陷", "bug", "故障", "根因", "root cause", "诊断", "suspected")
        requirement_keywords = ("需求", "requirement", "一致性")

        if any(keyword in query_lower or keyword in query for keyword in defect_keywords):
            return "defect_diagnosis"
        if any(keyword in query_lower or keyword in query for keyword in risk_keywords):
            return "risk_analysis"
        if any(keyword in query_lower or keyword in query for keyword in test_keywords):
            return "test_case_generation"
        if any(keyword in query_lower or keyword in query for keyword in requirement_keywords):
            return "requirement_analysis"
        if "误触发" in query:
            return "defect_diagnosis"
        return "general_qa"

    def _detect_function(self, query: str, query_lower: str) -> str | None:
        if "aeb" in query_lower or "自动紧急制动" in query or "紧急制动" in query:
            return "AEB"
        if "lka" in query_lower or "车道保持" in query:
            return "LKA"
        if "bms" in query_lower or "电池管理" in query or "电池" in query:
            return "BMS"
        return None
