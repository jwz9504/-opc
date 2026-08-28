from __future__ import annotations

from fastapi import FastAPI, Header, HTTPException

from .dto import MeetingCreate, ResumeRequest
from .service import MeetingService

app = FastAPI(title="Agent Meeting API", version="0.1.0")
service = MeetingService()


def require_token(authorization: str | None) -> None:
    if authorization != "Bearer dev-token":
        raise HTTPException(status_code=401, detail="invalid or missing token")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/meetings")
def create_meeting(payload: MeetingCreate, x_request_id: str = Header(...), authorization: str | None = Header(None)):
    require_token(authorization)
    return service.create(payload, x_request_id)


@app.get("/meetings/{meeting_id}")
def get_meeting(meeting_id: str, actor_id: str, authorization: str | None = Header(None)):
    require_token(authorization)
    try:
        service._authorized(meeting_id, actor_id)
        return service.view(meeting_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="meeting not found") from None
    except PermissionError:
        raise HTTPException(status_code=403, detail="meeting access denied") from None


@app.post("/meetings/{meeting_id}/run")
def run_meeting(meeting_id: str, actor_id: str, authorization: str | None = Header(None)):
    require_token(authorization)
    try:
        return service.run(meeting_id, actor_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="meeting not found") from None


@app.post("/meetings/{meeting_id}/resume")
def resume_meeting(meeting_id: str, payload: ResumeRequest, authorization: str | None = Header(None)):
    require_token(authorization)
    try:
        return service.resume(meeting_id, payload)
    except KeyError:
        raise HTTPException(status_code=404, detail="meeting not found") from None
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from None
