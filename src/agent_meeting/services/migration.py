from __future__ import annotations

from pathlib import Path

from alembic.config import Config

from alembic import command


def migrate(database: Path) -> None:
    database.parent.mkdir(parents=True, exist_ok=True)
    database.touch(exist_ok=True)
    config = Config(str(Path(__file__).parents[3] / "alembic.ini"))
    config.set_main_option("sqlalchemy.url", f"sqlite:///{database.as_posix()}")
    command.upgrade(config, "head")
