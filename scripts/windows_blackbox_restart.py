from __future__ import annotations

import subprocess
import time
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[1]
BASE = "http://127.0.0.1:8765"
TOKEN = "dev-token"


def main() -> None:
    process = subprocess.Popen(["python", "-m", "uvicorn", "agent_meeting.api.app:app", "--host", "127.0.0.1", "--port", "8765"], cwd=ROOT)
    try:
        for _ in range(30):
            try:
                if httpx.get(f"{BASE}/health").status_code == 200:
                    break
            except httpx.HTTPError:
                time.sleep(0.2)
        headers = {"Authorization": f"Bearer {TOKEN}", "X-Request-ID": "blackbox-1"}
        response = httpx.post(f"{BASE}/meetings", headers=headers, json={"question": "黑盒重启验收", "owner_id": "blackbox"})
        response.raise_for_status()
        meeting_id = response.json()["meeting_id"]
        httpx.post(f"{BASE}/meetings/{meeting_id}/run?actor_id=blackbox", headers=headers).raise_for_status()
        process.terminate()
        process.wait(timeout=10)
        process = subprocess.Popen(["python", "-m", "uvicorn", "agent_meeting.api.app:app", "--host", "127.0.0.1", "--port", "8765"], cwd=ROOT)
        for _ in range(30):
            try:
                if httpx.get(f"{BASE}/health").status_code == 200:
                    break
            except httpx.HTTPError:
                time.sleep(0.2)
        restored = httpx.get(f"{BASE}/meetings/{meeting_id}?actor_id=blackbox", headers=headers)
        restored.raise_for_status()
        print(restored.json())
    finally:
        process.terminate()
        process.wait(timeout=10)


if __name__ == "__main__":
    main()
