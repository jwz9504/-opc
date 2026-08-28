from __future__ import annotations

import json
from datetime import UTC, datetime
from hashlib import sha256
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

Validity = Literal["active", "stale", "stale_pending_review", "superseded", "invalid"]

class GovernanceVersion(BaseModel):
    model_config = ConfigDict(frozen=True)
    version_id: str
    status: Literal["draft", "confirmed", "frozen"] = "draft"
    payload: dict[str, Any] = Field(default_factory=dict)

class ScopeVersion(GovernanceVersion): pass
class AgendaVersion(GovernanceVersion): pass
class EvaluationPolicyVersion(GovernanceVersion):
    hard_gates: tuple[str, ...] = ()
    shortlist_limit: int = 5
    max_rework_rounds: int = 3

class ArtifactEnvelope(BaseModel):
    artifact_id: str
    artifact_type: str
    artifact_version: int = 1
    scope_version_id: str
    agenda_version_id: str
    evaluation_policy_version_id: str
    parent_artifact_ids: list[str] = Field(default_factory=list)
    producer_role: str
    producer_run_id: str
    model_id: str | None = None
    prompt_version: str | None = None
    tool_execution_ids: list[str] = Field(default_factory=list)
    content_hash: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    validity: Validity = "active"
    invalidation_reasons: list[str] = Field(default_factory=list)

class Evidence(BaseModel):
    envelope: ArtifactEnvelope
    claim_ids: list[str] = Field(default_factory=list)
    source_snapshot_id: str
    excerpt: str

class SourceSnapshot(BaseModel):
    envelope: ArtifactEnvelope
    uri: str
    content_hash: str
    retrieved_at: datetime

class Claim(BaseModel):
    envelope: ArtifactEnvelope
    text: str
    status: Literal["verified", "disputed", "unverified"]
    evidence_ids: list[str] = Field(default_factory=list)

class Proposal(BaseModel):
    envelope: ArtifactEnvelope
    title: str
    rationale: str
    constraint_ids: list[str] = Field(default_factory=list)
    provenance: list[str] = Field(default_factory=list)
    status: Literal["raw", "normalized", "ineligible", "eligible", "shortlisted", "selected", "pareto_candidate", "rejected"] = "raw"

class Critique(BaseModel):
    envelope: ArtifactEnvelope
    target_artifact_id: str
    category: Literal["factual", "feasibility", "risk", "compliance", "actionability", "writing"]
    severity: Literal["low", "medium", "high", "critical"]
    failure_scenario: str
    recommendation: str
    author_role: str

class CritiqueResolutionEvent(BaseModel):
    event_id: str
    critique_id: str
    action: Literal["addressed", "verified", "invalid", "duplicate", "not_applicable", "accepted_risk", "reopened"]
    actor_role: str
    revision_id: str | None = None
    verification_artifact_id: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @model_validator(mode="after")
    def validate_event(self) -> CritiqueResolutionEvent:
        if self.action == "addressed" and not self.revision_id:
            raise ValueError("addressed requires revision_id")
        if self.action == "verified" and not self.verification_artifact_id:
            raise ValueError("verified requires verification_artifact_id")
        if self.action == "accepted_risk" and self.actor_role != "human_owner":
            raise ValueError("accepted_risk requires human_owner")
        return self

class HumanDecision(BaseModel):
    envelope: ArtifactEnvelope
    actor_id: str
    decision: Literal["confirm", "select", "accept_risk", "approve", "reject", "cancel", "modify"]
    rationale: str

class GateResult(BaseModel):
    envelope: ArtifactEnvelope
    gate: str
    result: Literal["pass", "fail", "unknown"]
    authority: str
    rationale: str
    verification_artifact_id: str

class SoftEvaluation(BaseModel):
    envelope: ArtifactEnvelope
    dimension: str
    result: Literal["poor", "acceptable", "good", "excellent", "abstain"]
    evaluator_role: str

class ReportRevision(BaseModel):
    envelope: ArtifactEnvelope
    revision_kind: Literal["baseline", "candidate", "frozen_final"]
    sections: dict[str, str] = Field(default_factory=dict)
    statement_ids: list[str] = Field(default_factory=list)

class ReportStatement(BaseModel):
    envelope: ArtifactEnvelope
    sentence_id: str
    text: str
    claim_ids: list[str] = Field(default_factory=list)

class ActionItem(BaseModel):
    envelope: ArtifactEnvelope
    text: str
    owner: str = "待人工指定"
    acceptance_criteria: str

class MinorityOpinion(BaseModel):
    envelope: ArtifactEnvelope
    text: str
    author_role: str

class ProposalComparison(BaseModel):
    envelope: ArtifactEnvelope
    proposal_a_id: str
    proposal_b_id: str
    outcome: Literal["a_preferred", "b_preferred", "tie", "depends"]
    dimensions: dict[str, str] = Field(default_factory=dict)
    confidence: float = Field(ge=0, le=1)
    decisive_factors: list[str] = Field(default_factory=list)
    dependencies: list[str] = Field(default_factory=list)
    disagreement: list[str] = Field(default_factory=list)


class ProposalDisposition(BaseModel):
    envelope: ArtifactEnvelope
    proposal_id: str
    disposition: Literal["eligible", "ineligible", "shortlisted", "selected", "pareto_candidate", "rejected"]
    reasons: list[str] = Field(default_factory=list)


class ReworkPlan(BaseModel):
    envelope: ArtifactEnvelope
    target_critique_ids: list[str] = Field(default_factory=list)
    target_sections: list[str] = Field(default_factory=list)
    expected_improvements: list[str] = Field(default_factory=list)
    protected_dimensions: list[str] = Field(default_factory=list)
    allowed_tradeoffs: list[str] = Field(default_factory=list)
    responsible_role: str
    acceptance_criteria: list[str] = Field(default_factory=list)


class RegressionFinding(BaseModel):
    envelope: ArtifactEnvelope
    dimension: str
    severity: Literal["low", "high", "hard"]
    message: str
    blocking: bool = True


class GroundingFinding(BaseModel):
    envelope: ArtifactEnvelope
    sentence_id: str
    result: Literal["entailed", "partially_supported", "contradicted", "unrelated", "insufficient"]
    message: str
    claim_ids: list[str] = Field(default_factory=list)
    evidence_ids: list[str] = Field(default_factory=list)


class DecisionRecord(BaseModel):
    envelope: ArtifactEnvelope
    selected_proposal_id: str | None = None
    rationale: str
    rejected_proposal_ids: list[str] = Field(default_factory=list)


def content_hash(value: Any) -> str:
    data = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str)
    return sha256(data.encode("utf-8")).hexdigest()

def require_governance(envelope: ArtifactEnvelope, ids: tuple[str, str, str]) -> None:
    if (envelope.scope_version_id, envelope.agenda_version_id, envelope.evaluation_policy_version_id) != ids:
        raise ValueError("artifact governance versions do not match")
