## Production Acceptance Record

- Environment: Windows native single process
- Runtime: FastAPI + Uvicorn via uv
- Persistence: SQLite, SQLAlchemy ORM baseline, Alembic migration, LangGraph SQLite Checkpoint
- Model: Stub
- Acceptance: `uv run python scripts/windows_blackbox_restart.py`
- Backup: `uv run python scripts/backup-sqlite.py`
- Integrity: `uv run python scripts/check-sqlite.py`
- Quality: `pytest -q`, `ruff check .`, `mypy src`
- Status: Accepted for single-machine internal MVP; real model provider and production identity provider remain out of scope.
