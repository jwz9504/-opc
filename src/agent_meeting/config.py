from __future__ import annotations

import os
from pathlib import Path


def database_path() -> Path:
    return Path(os.getenv("AGENT_MEETING_DATABASE", "data/meetings.db"))


def artifact_path() -> Path:
    return Path(os.getenv("AGENT_MEETING_ARTIFACT_DIR", "data/artifacts"))


def report_path() -> Path:
    return Path(os.getenv("AGENT_MEETING_REPORT_DIR", "data/reports"))


def api_token() -> str:
    token = os.getenv("AGENT_MEETING_API_TOKEN", "dev-token")
    if os.getenv("AGENT_MEETING_ENV", "dev") == "prod" and token == "dev-token":
        raise RuntimeError("AGENT_MEETING_API_TOKEN must be set in prod")
    return token


def ensure_data_directories() -> None:
    database_path().parent.mkdir(parents=True, exist_ok=True)
    artifact_path().mkdir(parents=True, exist_ok=True)
    report_path().mkdir(parents=True, exist_ok=True)
