from __future__ import annotations

import subprocess
from pathlib import Path


def migrate(database: Path) -> None:
    database.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["alembic", "-x", f"db={database}", "upgrade", "head"], check=True)
