from agent_meeting.policies.decision import *
from agent_meeting.schemas.artifacts import *


def envelope(kind='x'):
    return ArtifactEnvelope(artifact_id=kind, artifact_type=kind, scope_version_id='s', agenda_version_id='a', evaluation_policy_version_id='e', producer_role='researcher', producer_run_id='r', content_hash='h')


def test_hash_stable():
    assert content_hash({'b': 1, 'a': 2}) == content_hash({'a': 2, 'b': 1})


def test_addressed_requires_revision():
    import pytest
    with pytest.raises(ValueError):
        CritiqueResolutionEvent(event_id='1', critique_id='c', action='addressed', actor_role='editor')


def test_hard_gate_wins():
    g = GateResult(envelope=envelope('g'), gate='factual', result='fail', authority='researcher', rationale='x', verification_artifact_id='v')
    assert aggregate_gates([g], {'factual'}) == 'reject'


def test_freeze_requires_human():
    assert not can_freeze(gate_status='pass', unresolved_critical=0, human_approved=False)
