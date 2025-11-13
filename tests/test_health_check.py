# tests/test_health_checks.py

import json
from pathlib import Path
from typing import Any, Dict

from scripts.python import health_checks


class DummyCursor:
    def __init__(self) -> None:
        self._step = 0

    def execute(self, sql: str) -> None:
        self._step += 1

    def fetchone(self) -> Dict[str, Any]:
        if self._step == 1:
            return {"sessions": 5}
        if self._step == 2:
            return {"total_db_size": 1024 * 1024}
        if self._step == 3:
            return {"locks_count": 0}
        return {"sessions": 0}


class DummyConn:
    def cursor(self, cursor_factory=None):
        return DummyCursor()

    def close(self) -> None:
        pass


class DummyContextManager:
    def __init__(self) -> None:
        self.conn = DummyConn()

    def __enter__(self) -> DummyConn:
        return self.conn

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.conn.close()


def test_postgres_basic_metrics(monkeypatch) -> None:
    monkeypatch.setattr(health_checks, "pg_connection", lambda autocommit=True: DummyContextManager())

    metrics = health_checks.postgres_basic_metrics()

    assert metrics["sessions_total"] == 5
    assert metrics["total_db_size_bytes"] == 1024 * 1024
    assert metrics["locks_count"] == 0


def test_write_health_status(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(health_checks, "BASE_DIR", tmp_path)

    payload = {"status": {"ok": True}, "metrics": {}, "timestamp": 123.0}
    health_checks.write_health_status(payload)

    out_file = tmp_path / "monitoring" / "status" / "health_status.json"
    assert out_file.exists()

    content = json.loads(out_file.read_text(encoding="utf-8"))
    assert content["status"]["ok"] is True
