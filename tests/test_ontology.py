from autodev_rag.config import SCHEMA_PATH
from autodev_rag.ontology import load_ontology


def test_load_ontology_contains_required_entities_and_relations() -> None:
    ontology = load_ontology(SCHEMA_PATH)

    for entity_type in ["Requirement", "Function", "Signal", "TestCase", "Risk", "Defect"]:
        assert ontology.validate_entity_type(entity_type)

    assert len(ontology.relations) >= 6
    assert set(ontology.get_relation_names()) >= {
        "implements",
        "verifies",
        "affects",
        "mitigated_by",
        "violates",
        "used_by",
    }

