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
    """
    Lance un backup PostgreSQL si la configuration le permet.

    Si config_global.yml est absent ou ne contient pas 'backup.postgres',
    on log un warning et on ne fait rien (retourne Path() vide).
    """
    global_cfg = load_config_global() or {}
    pg_cfg = load_config_postgres() or {}

    backup_root_cfg = global_cfg.get("backup", {})
    pg_backup_cfg = backup_root_cfg.get("postgres")

    if not pg_backup_cfg:
        logger.warning(
            "Aucune configuration 'backup.postgres' trouvée dans config_global.yml – "
            "aucune sauvegarde PostgreSQL exécutée."
        )
        return Path()

    conn = pg_cfg.get("connection")
    if not conn:
        logger.warning(
            "Aucune section 'connection' dans la configuration PostgreSQL – "
            "impossible de lancer le backup."
        )
        return Path()

    if not pg_backup_cfg.get("enabled", True):
        logger.info("Backup PostgreSQL désactivé dans la configuration")
        return Path()

    # Répertoire de backup : soit celui de la config, soit un répertoire par défaut
    backup_dir = Path(pg_backup_cfg.get("dir", str(BASE_DIR / "backups" / "postgres")))
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
    """
    Orchestration des backups.

    Si la section 'backup' n'existe pas, on sort proprement sans lever d'erreur.
    """
    cfg = load_config_global() or {}

    backup_cfg = cfg.get("backup")
    if not backup_cfg:
        logger.warning(
            "Aucune section 'backup' trouvée dans config_global.yml – "
            "aucun job de sauvegarde exécuté."
        )
        return

    # Backup PostgreSQL
    pg_backup = backup_postgres()
    if pg_backup:
        pg_cfg = backup_cfg.get("postgres", {})
        backup_dir = Path(pg_cfg.get("dir", str(BASE_DIR / "backups" / "postgres")))
        retention = int(pg_cfg.get("retention_days", 7))
        rotate_backups(backup_dir, retention)


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
