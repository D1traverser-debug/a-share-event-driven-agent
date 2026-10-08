from __future__ import annotations

import sqlite3
from pathlib import Path

from .models import MarketDayState


class SQLiteStateStore:
    def __init__(self, path: str | Path = "ashare_event_state.db"):
        self.path = str(path)

    def _connect(self) -> sqlite3.Connection:
        Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.path)
        conn.execute("CREATE TABLE IF NOT EXISTS runs (task_id TEXT PRIMARY KEY, payload TEXT NOT NULL, updated_at TEXT NOT NULL)")
        return conn

    def save(self, state: MarketDayState) -> None:
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO runs(task_id,payload,updated_at) VALUES(?,?,?) ON CONFLICT(task_id) DO UPDATE SET payload=excluded.payload,updated_at=excluded.updated_at",
                (state.contract.task_id, state.model_dump_json(), state.updated_at.isoformat()),
            )

    def load(self, task_id: str) -> MarketDayState | None:
        with self._connect() as conn:
            row = conn.execute("SELECT payload FROM runs WHERE task_id=?", (task_id,)).fetchone()
        return MarketDayState.model_validate_json(row[0]) if row else None

    def list_recent(self, limit: int = 20) -> list[MarketDayState]:
        with self._connect() as conn:
            rows = conn.execute("SELECT payload FROM runs ORDER BY updated_at DESC LIMIT ?", (max(1, min(limit, 100)),)).fetchall()
        return [MarketDayState.model_validate_json(row[0]) for row in rows]
