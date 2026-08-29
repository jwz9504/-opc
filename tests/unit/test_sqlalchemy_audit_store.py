from pathlib import Path

from agent_meeting.services.sqlalchemy_audit_store import SQLAlchemyAuditStore


def test_audit_store_roundtrip(tmp_path: Path) -> None:
    store = SQLAlchemyAuditStore(tmp_path / "audit.db")
    store.append("m1", "u1", "run", {"phase": "intake"})
    events = store.list("m1")
    assert len(events) == 1
    assert events[0]["action"] == "run"
    store.close()
