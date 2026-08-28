from __future__ import annotations

from agent_meeting.policies.critique import create_rework_plan
from agent_meeting.policies.regression import deterministic_regression, regression_route
from agent_meeting.schemas.artifacts import ArtifactEnvelope, Critique, ReportRevision


def env(identifier: str, kind: str) -> ArtifactEnvelope:
    return ArtifactEnvelope(artifact_id=identifier, artifact_type=kind, scope_version_id="s", agenda_version_id="a", evaluation_policy_version_id="e", producer_role="editor", producer_run_id="r", content_hash=identifier)


def test_rework_plan_and_authority():
    critique = Critique(envelope=env("c", "critique"), target_artifact_id="baseline", category="risk", severity="high", failure_scenario="failure", recommendation="add mitigation", author_role="red_team")
    plan = create_rework_plan(critique, env("rw", "rework"))
    assert plan.target_critique_ids == ["c"]


def test_candidate_hard_regression():
    baseline = ReportRevision(envelope=env("b", "revision"), revision_kind="baseline", sections={"decision_record": "keep", "action_items": "x", "evidence_appendix": "y"}, statement_ids=["s1"])
    candidate = ReportRevision(envelope=env("c", "revision"), revision_kind="candidate", sections={"action_items": "x"}, statement_ids=[])
    findings = deterministic_regression(baseline, candidate, protected_sections=["decision_record"])
    assert regression_route(findings) == "revise"
