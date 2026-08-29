from __future__ import annotations

from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import FileResponse, PlainTextResponse

from ..config import api_token
from .dto import MeetingCreate, MeetingView, ResumeRequest, SelectionRequest
from .service import MeetingService

app = FastAPI(title="Agent Meeting API", version="0.1.0")
service = MeetingService()


def require_token(authorization: str | None) -> None:
    if authorization != f"Bearer {api_token()}":
        raise HTTPException(status_code=401, detail="invalid or missing token")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/meetings")
def create_meeting(payload: MeetingCreate, x_request_id: str = Header(...), authorization: str | None = Header(None)) -> MeetingView:
    require_token(authorization)
    return service.create(payload, x_request_id)


@app.get("/meetings/{meeting_id}")
def get_meeting(meeting_id: str, actor_id: str, authorization: str | None = Header(None)) -> MeetingView:
    require_token(authorization)
    try:
        service._authorized(meeting_id, actor_id)
        return service.view(meeting_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="meeting not found") from None
    except PermissionError:
        raise HTTPException(status_code=403, detail="meeting access denied") from None


@app.post("/meetings/{meeting_id}/run")
def run_meeting(meeting_id: str, actor_id: str, authorization: str | None = Header(None)) -> MeetingView:
    require_token(authorization)
    try:
        return service.run(meeting_id, actor_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="meeting not found") from None


@app.post("/meetings/{meeting_id}/resume")
def resume_meeting(meeting_id: str, payload: ResumeRequest, authorization: str | None = Header(None)) -> MeetingView:
    require_token(authorization)
    try:
        return service.resume(meeting_id, payload)
    except KeyError:
        raise HTTPException(status_code=404, detail="meeting not found") from None
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from None


@app.post("/meetings/{meeting_id}/select")
def select_meeting_proposal(meeting_id: str, payload: SelectionRequest, authorization: str | None = Header(None)) -> MeetingView:
    require_token(authorization)
    try:
        return service.select_proposal(meeting_id, payload)
    except KeyError:
        raise HTTPException(status_code=404, detail="meeting not found") from None
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from None
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from None


def cancel_meeting(meeting_id: str, actor_id: str, authorization: str | None = Header(None)) -> MeetingView:
    require_token(authorization)
    try:
        return service.cancel(meeting_id, actor_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="meeting not found") from None
    except PermissionError:
        raise HTTPException(status_code=403, detail="meeting access denied") from None


@app.get("/meetings/{meeting_id}/report")
def get_report(meeting_id: str, actor_id: str, authorization: str | None = Header(None)) -> dict[str, object]:
    require_token(authorization)
    try:
        return service.report(meeting_id, actor_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="meeting not found") from None
    except PermissionError:
        raise HTTPException(status_code=403, detail="meeting access denied") from None


@app.get("/meetings/{meeting_id}/report.md", response_class=PlainTextResponse)
def download_report(meeting_id: str, actor_id: str, authorization: str | None = Header(None)) -> FileResponse:
    require_token(authorization)
    try:
        service._authorized(meeting_id, actor_id)
        service.report(meeting_id, actor_id)
        stored = service.reports.get(meeting_id)
        if stored is None:
            raise HTTPException(status_code=404, detail="report not found")
        return FileResponse(stored["markdown_path"], media_type="text/markdown", filename=f"{meeting_id}.md")
    except KeyError:
        raise HTTPException(status_code=404, detail="meeting not found") from None


@app.get("/meetings/{meeting_id}/report.json")
def download_report_json(meeting_id: str, actor_id: str, authorization: str | None = Header(None)) -> dict[str, object]:
    require_token(authorization)
    try:
        return service.report(meeting_id, actor_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="meeting not found") from None
    except PermissionError:
        raise HTTPException(status_code=403, detail="meeting access denied") from None


@app.get("/meetings/{meeting_id}/audit")
def get_audit(meeting_id: str, actor_id: str, authorization: str | None = Header(None)) -> list[dict[str, object]]:
    require_token(authorization)
    try:
        return service.audit_events(meeting_id, actor_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="meeting not found") from None
    except PermissionError:
        raise HTTPException(status_code=403, detail="meeting access denied") from None
