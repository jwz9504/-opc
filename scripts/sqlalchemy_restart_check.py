import subprocess
import sys
import time
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[1]
BASE = "http://127.0.0.1:8766"


def main() -> None:
    process = subprocess.Popen([sys.executable, "-m", "uvicorn", "agent_meeting.api.app:app", "--host", "127.0.0.1", "--port", "8766"], cwd=ROOT)
    try:
        for _ in range(40):
            try:
                if httpx.get(f"{BASE}/health", timeout=1).status_code == 200:
                    break
            except httpx.HTTPError:
                time.sleep(0.25)
        headers = {"Authorization": "Bearer dev-token", "X-Request-ID": f"orm-{time.time_ns()}"}
        response = httpx.post(f"{BASE}/meetings", headers=headers, json={"question": "ORM 重启验收", "owner_id": "orm"})
        response.raise_for_status()
        meeting_id = response.json()["meeting_id"]
        process.terminate()
        process.wait(timeout=10)
        process = subprocess.Popen([sys.executable, "-m", "uvicorn", "agent_meeting.api.app:app", "--host", "127.0.0.1", "--port", "8766"], cwd=ROOT)
        for _ in range(40):
            try:
                if httpx.get(f"{BASE}/health", timeout=1).status_code == 200:
                    break
            except httpx.HTTPError:
                time.sleep(0.25)
        restored = httpx.get(f"{BASE}/meetings/{meeting_id}?actor_id=orm", headers=headers)
        restored.raise_for_status()
        print(restored.json())
    finally:
        process.terminate()
        process.wait(timeout=10)


if __name__ == "__main__":
    main()
