from __future__ import annotations

import os

from fastapi import HTTPException

from .app import app as api_app

app = api_app


def expected_api_token() -> str:
    return os.getenv("AGENT_MEETING_API_TOKEN", "dev-token")


def require_configured_token(authorization: str | None) -> None:
    if authorization != f"Bearer {expected_api_token()}":
        raise HTTPException(status_code=401, detail="invalid or missing token")
