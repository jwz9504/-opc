from agent_meeting.policies.recovery import fan_in_ready, retry_failed
from agent_meeting.schemas.operations import BranchTask, OperationRecord, OutboxEvent
from agent_meeting.services.operations import OperationLedger, Outbox, idempotency_key


def test_idempotency_and_ledger():
    key = idempotency_key("t", "c", "search", {"q": "x"}, "read")
    ledger = OperationLedger()
    record = OperationRecord(operation_id="op", meeting_id="t", idempotency_key=key, operation_type="read")
    assert ledger.plan(record).operation_id == ledger.plan(record).operation_id


def test_outbox_deduplicates_and_confirms():
    outbox = Outbox()
    event = OutboxEvent(event_id="e", operation_id="op")
    outbox.enqueue(event)
    outbox.enqueue(event)
    assert len(outbox.pending()) == 1
    assert outbox.confirm("e").status == "confirmed"


def test_required_and_optional_branches():
    tasks = [BranchTask(task_id="1", branch_name="research", status="succeeded"), BranchTask(task_id="2", branch_name="optional", required=False, status="failed")]
    assert fan_in_ready(tasks)
    assert retry_failed(tasks)[0].attempts == 1
