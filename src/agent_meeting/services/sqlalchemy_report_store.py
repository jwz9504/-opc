from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .orm import create_engine_and_session
from .report_renderer import render_json, render_markdown
from .sqlalchemy_repository import SQLAlchemyRepository


class SQLAlchemyReportStore:
    def __init__(self, database: str | Path = "data/meetings.db", root: str | Path = "data/reports") -> None:
        self.engine, self.session_factory = create_engine_and_session(f"sqlite:///{Path(database).as_posix()}")
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def save(self, meeting_id: str, data: dict[str, Any]) -> dict[str, str]:
        markdown_path = self.root / f"{meeting_id}.md"
        markdown_path.write_text(render_markdown(data), encoding="utf-8")
        with self.session_factory() as session:
            SQLAlchemyRepository(session).save_report(meeting_id, data, str(markdown_path))
        return {"meeting_id": meeting_id, "markdown_path": str(markdown_path), "json": render_json(data)}

    def get(self, meeting_id: str) -> dict[str, Any] | None:
        with self.session_factory() as session:
            model = SQLAlchemyRepository(session).get_report(meeting_id)
            if model is None:
                return None
            data: dict[str, Any] = json.loads(model.payload)
            data["markdown_path"] = model.markdown_path
            return data

    def close(self) -> None:
        self.engine.dispose()
