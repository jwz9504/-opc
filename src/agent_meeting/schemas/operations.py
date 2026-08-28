from __future__ import annotations

from datetime import UTC, datetime
from typing import Literal

from pydantic import BaseModel, Field


class OperationRecord(BaseModel):
    operation_id: str
    meeting_id: str
    idempotency_key: str
    operation_type: str
    status: Literal["planned", "submitted", "succeeded", "failed"] = "planned"
    attempt: int = 0
    receipt: str | None = None
    error: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class OutboxEvent(BaseModel):
    event_id: str
    operation_id: str
    payload: dict[str, str] = Field(default_factory=dict)
    status: Literal["pending", "submitted", "confirmed", "failed", "dead_letter"] = "pending"
    attempts: int = 0


class BranchTask(BaseModel):
    task_id: str
    branch_name: str
    required: bool = True
    status: Literal["pending", "running", "succeeded", "failed"] = "pending"
    attempts: int = 0
    error: str | None = None
