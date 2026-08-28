from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class MeetingCreate(BaseModel):
    question: str = Field(min_length=1)
    owner_id: str = Field(min_length=1)

class ResumeRequest(BaseModel):
    decision: Literal["confirm", "approve", "reject", "revise"]
    actor_id: str
    token: str

class MeetingView(BaseModel):
    meeting_id: str
    owner_id: str
    phase: str
    human_pending: bool
