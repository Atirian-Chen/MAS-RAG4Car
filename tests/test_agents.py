from autodev_rag.agents import DomainExpertAgent, PlannerAgent, VerificationAgent
from autodev_rag.models import RetrievedChunk


def test_planner_detects_risk_and_function() -> None:
    planner = PlannerAgent()

    output = planner.plan("AEB 风险分析")

    assert output.intent == "risk_analysis"
    assert output.target_function == "AEB"


def test_planner_detects_test_generation_and_bms() -> None:
    planner = PlannerAgent()

    output = planner.plan("生成 BMS 高温测试用例")

    assert output.intent == "test_case_generation"
    assert output.target_function == "BMS"


def test_expert_and_verifier_outputs_are_grounded() -> None:
    planner_output = PlannerAgent().plan("AEB 风险分析")
    chunks = [
        RetrievedChunk(
            doc_id="06_risk_analysis_examples",
            chunk_id="chunk_001",
            text="RISK-AEB-002 与 REQ-AEB-003 相关，可通过 TC-AEB-RAIN-001 缓解。",
            score=0.9,
            metadata={"entity_type": "Risk", "function": "AEB"},
        )
    ]

    expert_output = DomainExpertAgent().answer("AEB 风险分析", planner_output, chunks)
    verifier_output = VerificationAgent().verify("AEB 风险分析", expert_output, chunks)

    assert expert_output.citations
    assert 0 <= verifier_output.groundedness_score <= 1
    assert 0 <= verifier_output.citation_coverage <= 1

