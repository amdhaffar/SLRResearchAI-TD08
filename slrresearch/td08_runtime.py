import json
from pathlib import Path

from .planning_models import EvidenceItem
from .quality_agent import evaluate_rules
from .quality_models import SharedState


def load_td08_artifacts(root: Path) -> tuple[list[EvidenceItem], set[str], dict, dict]:
    evidence_payload = json.loads((root / "artifacts" / "td06_evidence.json").read_text(encoding="utf-8"))
    writing_payload = json.loads((root / "artifacts" / "td07_writing_artifact.json").read_text(encoding="utf-8"))
    evidence = [EvidenceItem.model_validate(item) for item in evidence_payload["evidence"]]
    return evidence, set(evidence_payload["required_rqs"]), writing_payload["draft_report"], writing_payload["repaired_report"]


def build_state(report: dict, evidence: list[EvidenceItem], objective: str, budget: int = 6) -> SharedState:
    return SharedState(objective=objective, evidence_ids=[item.id for item in evidence], report=report, budget_left=budget)


def deterministic_evaluator(report: dict, evidence: list[EvidenceItem], required_rqs: set[str]):
    return evaluate_rules(report, evidence, required_rqs)


def artifact_writer(repaired_report: dict):
    def writer(_current: dict, _feedback: list[str]) -> dict:
        return repaired_report
    return writer


def build_artifact_workers(root: Path, evidence: list[EvidenceItem], draft: dict, repaired: dict):
    """Adapter les artefacts des TD précédents en workers observables."""
    def load_json(name: str) -> dict:
        return json.loads((root / "artifacts" / name).read_text(encoding="utf-8"))
    datasets = {name: load_json(filename) for name, filename in {
        "search": "search_results.json", "screening": "screening_decisions.json", "rag": "td06_evidence.json"
    }.items()}
    calls = {"writing": 0}
    def writing(_state):
        calls["writing"] += 1
        return repaired if calls["writing"] > 1 else draft
    return {
        "search": lambda _state: datasets["search"],
        "screening": lambda _state: datasets["screening"],
        "rag": lambda _state: datasets["rag"],
        "writing": writing,
        "quality": lambda state: state.report,
    }
