from agent_meeting.policies.grounding import grounding_blocks, semantic_finding, validate_structure
from agent_meeting.policies.quality import final_quality_decision
from agent_meeting.schemas.artifacts import (
 ArtifactEnvelope,
 Claim,
 GateResult,
 ReportStatement,
 SoftEvaluation,
)


def env(i: str, k: str, r: str = 'researcher') -> ArtifactEnvelope:
 return ArtifactEnvelope(artifact_id=i, artifact_type=k, scope_version_id='s', agenda_version_id='a', evaluation_policy_version_id='e', producer_role=r, producer_run_id='r', content_hash=i)

def test_structure():
 c=Claim(envelope=env('c','claim'), text='x', status='unverified')
 s=ReportStatement(envelope=env('st','statement','editor'), sentence_id='s1', text='确定事实', claim_ids=['c'])
 assert 'claim requires qualifier:c' in validate_structure([s], {'c':c})

def test_semantic():
 s=ReportStatement(envelope=env('s','statement'), sentence_id='s1', text='x')
 assert grounding_blocks([semantic_finding(s,'contradicted','conflict')])

def test_gate():
 g=GateResult(envelope=env('g','gate'), gate='factual', result='fail', authority='r', rationale='bad', verification_artifact_id='v')
 e=SoftEvaluation(envelope=env('e','soft'), dimension='creative', result='excellent', evaluator_role='ideator')
 assert final_quality_decision([g], {'factual'}, [e], human_approved=True)=='reject'
