import datetime as dt
import logging
import shutil
from pathlib import Path

from db_utils import BASE_DIR, load_config_global, load_config_postgres, run_subprocess

logger = logging.getLogger("db_admin.backup")


def _timestamp() -> str:
    return dt.datetime.now().strftime("%Y%m%d_%H%M%S")


def _ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def backup_postgres() -> Path:
    global_cfg = load_config_global()
    pg_cfg = load_config_postgres()
    backup_cfg = global_cfg["backup"]["postgres"]
    conn = pg_cfg["connection"]

    if not backup_cfg.get("enabled", True):
        logger.info("Backup PostgreSQL désactivé dans la configuration")
        return Path()

    backup_dir = Path(backup_cfg["dir"])
    _ensure_dir(backup_dir)

    filename = f"{conn['database']}_full_{_timestamp()}.dump"
    target = backup_dir / filename

    cmd = (
        f"PGPASSWORD='{conn['password']}' "
        f"pg_dump -h {conn['host']} -p {conn['port']} "
        f"-U {conn['user']} -F c -f '{target}' {conn['database']}"
    )

    run_subprocess(cmd)
    logger.info("Backup PostgreSQL créé: %s", target)
    return target


def rotate_backups(db_dir: Path, retention_days: int) -> None:
    if not db_dir.exists():
        return
    cutoff = dt.datetime.now() - dt.timedelta(days=retention_days)
    for path in db_dir.iterdir():
        if not path.is_file():
            continue
        mtime = dt.datetime.fromtimestamp(path.stat().st_mtime)
        if mtime < cutoff:
            logger.info("Suppression ancien backup: %s", path)
            path.unlink()


def run_all_backups() -> None:
    cfg = load_config_global()
    backup_cfg = cfg["backup"]

    pg_backup = backup_postgres()
    if pg_backup:
        rotate_backups(Path(backup_cfg["postgres"]["dir"]), backup_cfg["postgres"]["retention_days"])


def export_to_external_storage(source_dir: Path, external_dir: Path) -> None:
    if not source_dir.exists():
        return
    external_dir.mkdir(parents=True, exist_ok=True)
    for path in source_dir.iterdir():
        if path.is_file():
            dst = external_dir / path.name
            logger.info("Copie backup %s vers %s", path, dst)
            shutil.copy2(path, dst)


def main() -> None:
    logger.info("Démarrage des sauvegardes")
    run_all_backups()
    logger.info("Fin des sauvegardes")


if __name__ == "__main__":
    main()


