# tests/test_backup_runner.py

import os
import time
from pathlib import Path

from scripts.python import backup_runner


def _touch(path: Path, mtime: float) -> None:
    path.write_text("x", encoding="utf-8")
    os.utime(path, (mtime, mtime))


def test_rotate_backups_removes_old_files(tmp_path: Path) -> None:
    now = time.time()
    old_file = tmp_path / "old.dump"
    recent_file = tmp_path / "recent.dump"

    _touch(old_file, now - 10 * 24 * 3600)     
    _touch(recent_file, now - 1 * 24 * 3600)  

    backup_runner.rotate_backups(tmp_path, retention_days=7)

    assert not old_file.exists()
    assert recent_file.exists()
