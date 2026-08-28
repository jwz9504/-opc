from __future__ import annotations

import tempfile
from pathlib import Path

from fastapi.testclient import TestClient

from agent_meeting.api import app as app_module
from agent_meeting.api.service import MeetingService
from agent_meeting.services.sqlite_repository import SQLiteRepository


def test_http_meeting_lifecycle() -> None:
    with tempfile.TemporaryDirectory() as directory:
        service = MeetingService(SQLiteRepository(Path(directory) / "meetings.db"))
        original = app_module.service
        app_module.service = service
        try:
            client = TestClient(app_module.app)
            headers = {"Authorization": "Bearer dev-token", "X-Request-ID": "e2e-1"}
            response = client.post("/meetings", headers=headers, json={"question": "测试问题", "owner_id": "owner"})
            assert response.status_code == 200
            meeting_id = response.json()["meeting_id"]
            response = client.post(f"/meetings/{meeting_id}/run?actor_id=owner", headers=headers)
            assert response.status_code == 200
            assert response.json()["human_pending"] is True
            response = client.get(f"/meetings/{meeting_id}/audit?actor_id=owner", headers=headers)
            assert response.status_code == 200
            assert response.json()[0]["action"] == "meeting_created"
        finally:
            app_module.service = original
