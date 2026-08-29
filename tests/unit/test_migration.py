
from agent_meeting.config import database_path
from agent_meeting.services.migration import migrate


def test_migration_uses_configured_database(tmp_path, monkeypatch):
    path = tmp_path / "nested" / "custom.db"
    monkeypatch.setenv("AGENT_MEETING_DATABASE", str(path))
    migrate(database_path())
    assert path.exists()
