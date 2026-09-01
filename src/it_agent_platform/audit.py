import json
import sqlite3
from pathlib import Path
from threading import Lock
from typing import Any

from .models import utc_now


class AuditLog:
    def __init__(self, path: Path) -> None:
        self.path = path
        self._lock = Lock()
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS audit_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    workflow_id TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    actor TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )

    def record(
        self, workflow_id: str, event_type: str, actor: str, payload: dict[str, Any]
    ) -> None:
        serialized = json.dumps(payload, sort_keys=True, default=str)
        with self._lock, self._connect() as connection:
            connection.execute(
                "INSERT INTO audit_events (workflow_id, event_type, actor, payload, created_at) "
                "VALUES (?, ?, ?, ?, ?)",
                (workflow_id, event_type, actor, serialized, utc_now().isoformat()),
            )

    def list_events(self, workflow_id: str) -> list[dict[str, Any]]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT * FROM audit_events WHERE workflow_id = ? ORDER BY id", (workflow_id,)
            ).fetchall()
        return [{**dict(row), "payload": json.loads(row["payload"])} for row in rows]
