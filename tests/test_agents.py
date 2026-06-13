from autodev_rag.agents import DomainExpertAgent, PlannerAgent, VerificationAgent
from autodev_rag.models import ExpertOutput, RetrievedChunk


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


def test_expert_selects_citations_instead_of_citing_every_chunk() -> None:
    planner_output = PlannerAgent().plan("AEB 雨天误触发风险分析")
    chunks = [
        RetrievedChunk(
            doc_id=f"doc_{index}",
            chunk_id="chunk_000",
            text=text,
            score=1.0 - index * 0.1,
            metadata={"entity_type": entity_type, "function": "AEB"},
        )
        for index, (entity_type, text) in enumerate(
            [
                ("Risk", "RISK-AEB-002 雨天误触发风险与 REQ-AEB-003 相关。"),
                ("TestCase", "TC-AEB-RAIN-001 验证雨天反光误触发抑制。"),
                ("Requirement", "REQ-AEB-003 要求多源一致性检查。"),
                ("Signal", "SIG-VSP-001 vehicle_speed 用于低速场景判断。"),
                ("Defect", "BUG-AEB-001 记录雨天误触发现象。"),
            ]
        )
    ]

    expert_output = DomainExpertAgent().answer("AEB 雨天误触发风险分析", planner_output, chunks)

    assert expert_output.citations
    assert len(expert_output.citations) < len(chunks)
    assert len(expert_output.citations) <= DomainExpertAgent.MAX_CITATIONS


def test_verifier_penalizes_citing_every_retrieved_chunk() -> None:
    chunks = [
        RetrievedChunk(
            doc_id=f"doc_{index}",
            chunk_id="chunk_000",
            text=f"REQ-AEB-00{index} AEB 雨天误触发风险证据。",
            score=1.0,
            metadata={"entity_type": "Requirement", "function": "AEB"},
        )
        for index in range(1, 6)
    ]
    expert_output = ExpertOutput(
        answer="AEB 雨天误触发风险分析引用所有证据。",
        related_entities=["REQ-AEB-001"],
        citations=[chunk.citation for chunk in chunks],
        assumptions=[],
        missing_info=[],
    )

    verifier_output = VerificationAgent().verify("AEB 雨天误触发风险分析", expert_output, chunks)

    assert verifier_output.final_verdict != "pass"
    assert any("every retrieved chunk" in claim for claim in verifier_output.unsupported_claims)
