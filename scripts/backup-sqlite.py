import shutil
from datetime import UTC, datetime
from pathlib import Path

source = Path("data/meetings.db")
target_dir = Path("data/backups")
target_dir.mkdir(parents=True, exist_ok=True)
if not source.exists():
    raise SystemExit("database not found")
target = target_dir / f"meetings-{datetime.now(UTC):%Y%m%d-%H%M%S}.db"
shutil.copy2(source, target)
print(target)
