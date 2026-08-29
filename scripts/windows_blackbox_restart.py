from __future__ import annotations

import subprocess
import time
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[1]
BASE = "http://127.0.0.1:8765"
TOKEN = "dev-token"


def wait_ready() -> None:
    for _ in range(50):
        try:
            if httpx.get(f"{BASE}/health", timeout=1).status_code == 200:
                return
        except httpx.HTTPError:
            time.sleep(0.2)
    raise RuntimeError("Uvicorn did not become ready")


def main() -> None:
    process = subprocess.Popen(["python", "-m", "uvicorn", "agent_meeting.api.app:app", "--host", "127.0.0.1", "--port", "8765"], cwd=ROOT)
    try:
        wait_ready()
        headers = {"Authorization": f"Bearer {TOKEN}", "X-Request-ID": f"blackbox-{time.time_ns()}"}
        response = httpx.post(f"{BASE}/meetings", headers=headers, json={"question": "完整黑盒验收", "owner_id": "blackbox"})
        response.raise_for_status()
        meeting_id = response.json()["meeting_id"]
        httpx.post(f"{BASE}/meetings/{meeting_id}/run?actor_id=blackbox", headers=headers).raise_for_status()
        process.terminate()
        process.wait(timeout=10)
        process = subprocess.Popen(["python", "-m", "uvicorn", "agent_meeting.api.app:app", "--host", "127.0.0.1", "--port", "8765"], cwd=ROOT)
        wait_ready()
        restored = httpx.get(f"{BASE}/meetings/{meeting_id}?actor_id=blackbox", headers=headers)
        restored.raise_for_status()
        assert restored.json()["human_pending"] is True
        confirm = httpx.post(f"{BASE}/meetings/{meeting_id}/resume", headers=headers, json={"decision": "confirm", "actor_id": "blackbox", "token": "invalid"})
        assert confirm.status_code == 403
        report = httpx.get(f"{BASE}/meetings/{meeting_id}/report.json?actor_id=blackbox", headers=headers)
        report.raise_for_status()
        audit = httpx.get(f"{BASE}/meetings/{meeting_id}/audit?actor_id=blackbox", headers=headers)
        audit.raise_for_status()
        print({"meeting_id": meeting_id, "restored": restored.json(), "report_status": report.json().get("status"), "audit_events": len(audit.json())})
    finally:
        process.terminate()
        process.wait(timeout=10)


if __name__ == "__main__":
    main()
