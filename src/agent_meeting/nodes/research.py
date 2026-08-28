from __future__ import annotations

from ..schemas.artifacts import ArtifactEnvelope, Proposal


def stub_research(thread_id: str) -> list[str]:
    return [f"claim:{thread_id}:context", f"evidence:{thread_id}:source-1"]


def stub_ideation(thread_id: str) -> list[Proposal]:
    def env(identifier: str) -> ArtifactEnvelope:
        return ArtifactEnvelope(artifact_id=identifier, artifact_type="proposal", scope_version_id="s", agenda_version_id="a", evaluation_policy_version_id="e", producer_role="ideator", producer_run_id=thread_id, content_hash=identifier)
    return [
        Proposal(envelope=env(f"proposal:{thread_id}:1"), title="渐进式试点", rationale="先小范围验证，再逐步扩展", provenance=["ideation:1"]),
        Proposal(envelope=env(f"proposal:{thread_id}:2"), title="平台化重构", rationale="一次性建设统一能力底座", provenance=["ideation:2"]),
        Proposal(envelope=env(f"proposal:{thread_id}:3"), title="外部合作", rationale="借助成熟供应商缩短交付周期", provenance=["ideation:3"]),
    ]
