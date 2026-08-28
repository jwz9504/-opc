from __future__ import annotations

from collections.abc import Iterable

from ..schemas.artifacts import RegressionFinding, ReportRevision

REQUIRED_SECTIONS = {"decision_record", "action_items", "evidence_appendix"}


def deterministic_regression(
    baseline: ReportRevision,
    candidate: ReportRevision,
    *,
    protected_sections: Iterable[str] = (),
) -> list[RegressionFinding]:
    findings: list[RegressionFinding] = []
    missing = REQUIRED_SECTIONS - candidate.sections.keys()
    for section in sorted(missing):
        findings.append(RegressionFinding(envelope=candidate.envelope, dimension=section, severity="hard", message="required section missing"))
    for section in protected_sections:
        if baseline.sections.get(section) != candidate.sections.get(section):
            findings.append(RegressionFinding(envelope=candidate.envelope, dimension=section, severity="hard", message="protected section changed"))
    if not candidate.statement_ids:
        findings.append(RegressionFinding(envelope=candidate.envelope, dimension="statements", severity="hard", message="candidate has no statements"))
    return findings


def regression_route(findings: Iterable[RegressionFinding]) -> str:
    return "revise" if any(f.blocking for f in findings) else "promote"
