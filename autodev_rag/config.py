"""Project configuration defaults."""

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
DOCS_DIR = DATA_DIR / "docs"
SCHEMA_PATH = DATA_DIR / "schema" / "ontology.yaml"
EVAL_CASES_PATH = DATA_DIR / "eval" / "eval_cases.jsonl"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"
DEFAULT_INDEX_PATH = OUTPUTS_DIR / "index.pkl"

