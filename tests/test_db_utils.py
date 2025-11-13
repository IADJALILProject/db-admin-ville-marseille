# tests/test_db_utils.py

import textwrap
from pathlib import Path

import pytest

from scripts.python import db_utils


def test_load_yaml_reads_file(tmp_path: Path) -> None:
    content = textwrap.dedent(
        """
        key1: value1
        key2:
          nested: 123
        """
    )
    cfg_path = tmp_path / "config.yml"
    cfg_path.write_text(content, encoding="utf-8")

    cfg = db_utils.load_yaml(cfg_path)

    assert cfg["key1"] == "value1"
    assert cfg["key2"]["nested"] == 123


def test_get_postgres_conn_info_uses_config(monkeypatch) -> None:
    fake_cfg = {
        "connection": {
            "host": "db-host",
            "port": 5433,
            "database": "mairie_test",
            "user": "db_user",
            "password": "secret",
        }
    }

    monkeypatch.setattr(db_utils, "load_config_postgres", lambda: fake_cfg)

    info = db_utils.get_postgres_conn_info()

    assert info.host == "db-host"
    assert info.port == 5433
    assert info.database == "mairie_test"
    assert info.user == "db_user"
    assert info.password == "secret"


def test_run_subprocess_success(monkeypatch) -> None:
    class DummyResult:
        def __init__(self):
            self.returncode = 0
            self.stdout = "ok"
            self.stderr = ""

    def fake_run(*args, **kwargs):
        return DummyResult()

    monkeypatch.setattr("subprocess.run", fake_run)

    result = db_utils.run_subprocess("echo test")
    assert result.returncode == 0
