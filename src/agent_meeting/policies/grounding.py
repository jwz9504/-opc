from __future__ import annotations

from collections.abc import Iterable
from typing import Literal

from ..schemas.artifacts import Claim, Evidence, GroundingFinding, ReportStatement, SourceSnapshot

GroundingResult = Literal["entailed", "partially_supported", "contradicted", "unrelated", "insufficient"]


def validate_structure(
    statements: Iterable[ReportStatement],
    claims: dict[str, Claim],
    evidence: dict[str, Evidence] | None = None,
    snapshots: dict[str, SourceSnapshot] | None = None,
) -> list[str]:
    evidence = evidence or{}
    snapshots = snapshots or{}
    errors: list[str] = []
    for statement in statements:
        if not statement.sentence_id:
            errors.append("missing sentence_id")
        for claim_id in statement.claim_ids:
            claim = claims.get(claim_id)
            if claim is None:
                errors.append(f"missing claim:{claim_id}")
                continue
            for evidence_id in claim.evidence_ids:
                item = evidence.get(evidence_id)
                if item is None:
                    errors.append(f"missing evidence:{evidence_id}")
                elif item.source_snapshot_id not in snapshots:
                    errors.append(f"missing source_snapshot:{item.source_snapshot_id}")
            if claim.status in {"disputed", "unverified"} and not any(word in statement.text for word in ("可能", "尚未验证", "存在争议", "据现有证据")):
                errors.append(f"claim requires qualifier:{claim_id}")
    return errors


def semantic_finding(statement: ReportStatement, result: GroundingResult, message: str) -> GroundingFinding:
    return GroundingFinding(envelope=statement.envelope, sentence_id=statement.sentence_id, result=result, message=message, claim_ids=statement.claim_ids)


def grounding_blocks(findings: Iterable[GroundingFinding]) -> bool:
    return any(f.result in {"contradicted", "unrelated", "insufficient"} for f in findings)
