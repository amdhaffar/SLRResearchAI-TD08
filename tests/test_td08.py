from pathlib import Path

import pytest

from slrresearch.orchestrator import ALLOWED_TRANSITIONS, full_pipeline_run, full_supervisor_run, pipeline_run, supervisor_run, validate_handoff
from slrresearch.quality_agent import evaluate_rules, run_quality_loop
from slrresearch.quality_models import Handoff
from slrresearch.td08_runtime import artifact_writer, build_artifact_workers, build_state, load_td08_artifacts

ROOT = Path(__file__).parents[1]
EVIDENCE, REQUIRED_RQS, DRAFT, REPAIRED = load_td08_artifacts(ROOT)
OBJECTIVE = "Contrôler la fidélité de la note avant livraison."


def test_todo_1_parse_et_verifie_les_affirmations():
    report = evaluate_rules(DRAFT, EVIDENCE, REQUIRED_RQS)
    assert len(report.findings) == 5
    assert any(item.status == "unsupported" for item in report.findings)


def test_todo_2_couverture_des_rq():
    report = evaluate_rules(DRAFT, EVIDENCE, REQUIRED_RQS)
    assert report.rq_coverage == 1
    incomplete = {**DRAFT, "sections": DRAFT["sections"][:2]}
    assert evaluate_rules(incomplete, EVIDENCE, REQUIRED_RQS).rq_coverage < 1


def test_todo_3_citations_inconnues_refusees():
    bad = {**DRAFT, "claims": [*DRAFT["claims"], {"id": "AX", "rq_id": "RQ1", "text": "Une affirmation suffisamment longue.", "evidence_ids": ["E999"]}]}
    report = evaluate_rules(bad, EVIDENCE, REQUIRED_RQS)
    assert any(item.claim_id == "AX" and item.status == "unsupported" for item in report.findings)


def test_todo_4_verdict_revise_et_feedback():
    report = evaluate_rules(DRAFT, EVIDENCE, REQUIRED_RQS)
    assert report.verdict == "REVISE"
    assert report.feedback


def test_todo_5_boucle_bornee_accepte_apres_reparation():
    result = run_quality_loop(DRAFT, EVIDENCE, REQUIRED_RQS, artifact_writer(REPAIRED), max_revisions=1)
    assert result["quality"].verdict == "ACCEPT"
    assert len(result["history"]) == 2


def test_todo_6_boucle_echoue_escalade_si_budget_epuise():
    result = run_quality_loop(DRAFT, EVIDENCE, REQUIRED_RQS, lambda report, feedback: report, max_revisions=1)
    assert result["quality"].verdict == "ESCALATE"


def test_todo_7_handoff_respecte_les_permissions():
    handoff = Handoff(source="writing", target="quality", objective=OBJECTIVE, artifact=DRAFT, evidence_ids=["E1"], status="ok", budget_left=2)
    validate_handoff(handoff, ALLOWED_TRANSITIONS, {item.id for item in EVIDENCE})
    forbidden = handoff.model_copy(update={"target": "search"})
    with pytest.raises(PermissionError):
        validate_handoff(forbidden, ALLOWED_TRANSITIONS, {item.id for item in EVIDENCE})


def test_todo_8_pipeline_s_arrete_sans_revision():
    state = build_state(DRAFT, EVIDENCE, OBJECTIVE, budget=3)
    evaluate = lambda report: evaluate_rules(report, EVIDENCE, REQUIRED_RQS)
    result = pipeline_run(state, evaluate)
    assert result.status == "ESCALATE"
    assert result.transitions == ["writing→quality", "quality→escalate"]


def test_todo_9_superviseur_revise_et_termine():
    state = build_state(DRAFT, EVIDENCE, OBJECTIVE, budget=4)
    evaluate = lambda report: evaluate_rules(report, EVIDENCE, REQUIRED_RQS)
    result = supervisor_run(state, evaluate, artifact_writer(REPAIRED), max_handoffs=3)
    assert result.status == "FINISH"
    assert "quality→writing" in result.transitions
    assert result.state.quality.verdict == "ACCEPT"


def test_todo_10_pipeline_transmet_les_cinq_agents():
    result = full_pipeline_run(
        build_state(DRAFT, EVIDENCE, OBJECTIVE, budget=8),
        build_artifact_workers(ROOT, EVIDENCE, DRAFT, REPAIRED),
        lambda report: evaluate_rules(report, EVIDENCE, REQUIRED_RQS),
    )
    assert result.status == "ESCALATE"
    assert result.transitions[:4] == ["search→screening", "screening→rag", "rag→writing", "writing→quality"]
    assert {"search", "screening", "rag", "writing", "quality"} <= set(result.state.artifacts)


def test_todo_11_superviseur_reutilise_le_feedback():
    result = full_supervisor_run(
        build_state(DRAFT, EVIDENCE, OBJECTIVE, budget=8),
        build_artifact_workers(ROOT, EVIDENCE, DRAFT, REPAIRED),
        lambda report: evaluate_rules(report, EVIDENCE, REQUIRED_RQS),
        max_handoffs=8,
    )
    assert result.status == "FINISH"
    assert "quality→rag" in result.transitions
    assert "rag→writing" in result.transitions
    assert result.state.quality.verdict == "ACCEPT"
