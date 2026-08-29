import sqlite3
from pathlib import Path

path = Path("data/meetings.db")
if not path.exists():
    raise SystemExit("database not found")
with sqlite3.connect(path) as db:
    result = db.execute("PRAGMA integrity_check").fetchone()[0]
if result != "ok":
    raise SystemExit(f"integrity check failed: {result}")
print("ok")
