from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

from .report_renderer import render_json, render_markdown


class ReportRepository:
    def __init__(self, db: sqlite3.Connection, root: str | Path = "data/reports") -> None:
        self.db = db
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.db.execute("CREATE TABLE IF NOT EXISTS reports (meeting_id TEXT PRIMARY KEY, payload TEXT NOT NULL, markdown_path TEXT NOT NULL)")
        self.db.commit()

    def save(self, meeting_id: str, data: dict[str, Any]) -> dict[str, str]:
        markdown_path = self.root / f"{meeting_id}.md"
        markdown_path.write_text(render_markdown(data), encoding="utf-8")
        self.db.execute("INSERT OR REPLACE INTO reports VALUES (?, ?, ?)", (meeting_id, json.dumps(data, ensure_ascii=False, sort_keys=True), str(markdown_path)))
        self.db.commit()
        return {"meeting_id": meeting_id, "markdown_path": str(markdown_path), "json": render_json(data)}

    def get(self, meeting_id: str) -> dict[str, Any] | None:
        row = self.db.execute("SELECT payload, markdown_path FROM reports WHERE meeting_id=?", (meeting_id,)).fetchone()
        if row is None:
            return None
        data: dict[str, Any] = json.loads(row[0])
        data["markdown_path"] = row[1]
        return data
