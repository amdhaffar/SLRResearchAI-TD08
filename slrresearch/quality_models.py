from typing import Any, Literal

from pydantic import BaseModel, Field


class Claim(BaseModel):
    id: str
    rq_id: str
    text: str = Field(min_length=5)
    evidence_ids: list[str] = Field(default_factory=list)


class ClaimFinding(BaseModel):
    claim_id: str
    status: Literal["supported", "unsupported", "contradicted"]
    reason: str


class QualityReport(BaseModel):
    verdict: Literal["ACCEPT", "REVISE", "ESCALATE"]
    score: float = Field(ge=0, le=1)
    rq_coverage: float = Field(ge=0, le=1)
    citation_validity: float = Field(ge=0, le=1)
    faithfulness: float = Field(ge=0, le=1)
    findings: list[ClaimFinding] = Field(default_factory=list)
    feedback: list[str] = Field(default_factory=list)
    llm_calls: int = Field(default=0, ge=0)
    revision: int = Field(default=0, ge=0)
    repair_target: Literal["search", "screening", "rag", "writing", "human"] = "writing"


class QualityJudgeDecision(BaseModel):
    verdict: Literal["ACCEPT", "REVISE", "ESCALATE"]
    score: float = Field(ge=0, le=1)
    feedback: list[str] = Field(min_length=1)


class Handoff(BaseModel):
    source: str
    target: str
    objective: str = Field(min_length=10)
    artifact: dict[str, Any]
    evidence_ids: list[str] = Field(default_factory=list)
    status: Literal["ok", "partial", "blocked"]
    budget_left: int = Field(ge=0)


class SharedState(BaseModel):
    objective: str
    evidence_ids: list[str] = Field(default_factory=list)
    report: dict[str, Any] = Field(default_factory=dict)
    artifacts: dict[str, dict[str, Any]] = Field(default_factory=dict)
    quality: QualityReport | None = None
    next_agent: str = "quality"
    current_agent: str = "search"
    budget_left: int = Field(default=6, ge=0)
    history: list[str] = Field(default_factory=list)


class OrchestrationResult(BaseModel):
    pattern: Literal["pipeline", "supervisor"]
    status: Literal["FINISH", "ESCALATE", "BUDGET_EXHAUSTED"]
    state: SharedState
    handoffs: list[Handoff] = Field(default_factory=list)
    transitions: list[str] = Field(default_factory=list)
    actions: int = Field(default=0, ge=0)
