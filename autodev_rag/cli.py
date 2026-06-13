"""Typer CLI for AutoDev Multi-Agent RAG."""

from __future__ import annotations

import json
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from autodev_rag.agents import DomainExpertAgent, PlannerAgent, VerificationAgent
from autodev_rag.chunker import chunk_documents
from autodev_rag.config import DEFAULT_INDEX_PATH, DOCS_DIR, EVAL_CASES_PATH, OUTPUTS_DIR
from autodev_rag.document_loader import load_documents
from autodev_rag.evaluator import evaluate_all, load_eval_cases, save_eval_summary
from autodev_rag.pipeline import AutoDevRAGPipeline
from autodev_rag.vector_store import LocalVectorStore


app = typer.Typer(help="AutoDev Multi-Agent RAG command line interface.")
console = Console()


def _build_store(docs: Path, index: Path) -> LocalVectorStore:
    documents = load_documents(docs)
    chunks = chunk_documents(documents)
    store = LocalVectorStore()
    store.build(chunks)
    store.save(index)
    console.print(f"[green]Built index[/green]: {len(documents)} docs, {len(chunks)} chunks -> {index}")
    return store


def _load_or_build_store(docs: Path, index: Path) -> LocalVectorStore:
    if index.exists():
        return LocalVectorStore.load(index)
    console.print(f"[yellow]Index not found, building one at {index}[/yellow]")
    return _build_store(docs, index)


def _make_pipeline(store: LocalVectorStore) -> AutoDevRAGPipeline:
    return AutoDevRAGPipeline(
        vector_store=store,
        planner_agent=PlannerAgent(),
        expert_agent=DomainExpertAgent(),
        verifier_agent=VerificationAgent(),
    )


@app.command("build-index")
def build_index(
    docs: Path = typer.Option(DOCS_DIR, "--docs", help="Directory containing Markdown documents."),
    index: Path = typer.Option(DEFAULT_INDEX_PATH, "--index", help="Output index pickle path."),
) -> None:
    """Build the offline TF-IDF index."""
    _build_store(docs, index)


@app.command("ask")
def ask(
    query: str = typer.Argument(..., help="Engineering question to ask."),
    index: Path = typer.Option(DEFAULT_INDEX_PATH, "--index", help="Index pickle path."),
    docs: Path = typer.Option(DOCS_DIR, "--docs", help="Docs directory used when index is missing."),
    output_dir: Path = typer.Option(OUTPUTS_DIR, "--output-dir", help="Directory for reports and traces."),
    top_k: int = typer.Option(5, "--top-k", min=1, max=20, help="Number of chunks to retrieve."),
) -> None:
    """Run the multi-agent RAG pipeline for one query."""
    store = _load_or_build_store(docs, index)
    pipeline = _make_pipeline(store)
    trace = pipeline.run(query, top_k=top_k, output_dir=output_dir)

    table = Table(title="AutoDev RAG Result")
    table.add_column("Field")
    table.add_column("Value")
    table.add_row("intent", trace.planner_output.intent)
    table.add_row("target_function", trace.planner_output.target_function or "None")
    table.add_row("top_citations", ", ".join(trace.expert_output.citations[:5]))
    table.add_row("final_verdict", trace.verifier_output.final_verdict)
    table.add_row("report_path", trace.final_report_path)
    console.print(table)


@app.command("report")
def report(
    query: str = typer.Argument(..., help="Engineering question to ask."),
    index: Path = typer.Option(DEFAULT_INDEX_PATH, "--index", help="Index pickle path."),
    docs: Path = typer.Option(DOCS_DIR, "--docs", help="Docs directory used when index is missing."),
    output_dir: Path = typer.Option(OUTPUTS_DIR, "--output-dir", help="Directory for reports and traces."),
    top_k: int = typer.Option(5, "--top-k", min=1, max=20, help="Number of chunks to retrieve."),
) -> None:
    """Generate a Markdown report for one query."""
    ask(query=query, index=index, docs=docs, output_dir=output_dir, top_k=top_k)


@app.command("eval")
def eval_command(
    cases: Path = typer.Option(EVAL_CASES_PATH, "--cases", help="JSONL eval cases path."),
    index: Path = typer.Option(DEFAULT_INDEX_PATH, "--index", help="Index pickle path."),
    docs: Path = typer.Option(DOCS_DIR, "--docs", help="Docs directory used when index is missing."),
    output_dir: Path = typer.Option(OUTPUTS_DIR / "eval", "--output-dir", help="Directory for eval reports."),
) -> None:
    """Run small-scale offline evaluation."""
    store = _load_or_build_store(docs, index)
    pipeline = _make_pipeline(store)
    eval_cases = load_eval_cases(cases)
    summary = evaluate_all(pipeline, eval_cases, output_dir=output_dir)
    summary_path = save_eval_summary(summary, output_dir / "eval_summary.json")

    console.print(json.dumps({k: v for k, v in summary.items() if k != "results"}, ensure_ascii=False, indent=2))
    console.print(f"[green]Saved eval summary[/green]: {summary_path}")


if __name__ == "__main__":
    app()
