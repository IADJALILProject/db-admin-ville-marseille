import argparse
import logging
from pathlib import Path

from db_utils import load_config_postgres, run_subprocess

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)


def restore_postgres(backup_file: Path, drop_before: bool = True) -> None:
    cfg = load_config_postgres()["connection"]
    host = cfg["host"]
    port = cfg["port"]
    user = cfg["user"]
    password = cfg["password"]
    dbname = cfg["database"]

    if drop_before:
        logger.info("Arrêt des connexions actives sur la base %s", dbname)
        cmd_terminate = [
            "bash",
            "-lc",
            (
                f"PGPASSWORD='{password}' psql -h {host} -p {port} -U {user} -d postgres "
                f"-v ON_ERROR_STOP=1 "
                f"-c \"SELECT pg_terminate_backend(pid) "
                f"FROM pg_stat_activity "
                f"WHERE datname = '{dbname}' AND pid <> pg_backend_pid();\""
            ),
        ]
        run_subprocess(cmd_terminate)

        logger.info("Suppression de la base %s si elle existe", dbname)
        cmd_drop = [
            "bash",
            "-lc",
            (
                f"PGPASSWORD='{password}' psql -h {host} -p {port} -U {user} -d postgres "
                f"-v ON_ERROR_STOP=1 "
                f"-c \"DROP DATABASE IF EXISTS {dbname};\""
            ),
        ]
        run_subprocess(cmd_drop)

        logger.info("Création de la base %s", dbname)
        cmd_create = [
            "bash",
            "-lc",
            (
                f"PGPASSWORD='{password}' psql -h {host} -p {port} -U {user} -d postgres "
                f"-v ON_ERROR_STOP=1 "
                f"-c \"CREATE DATABASE {dbname};\""
            ),
        ]
        run_subprocess(cmd_create)

    logger.info("Restauration du dump %s dans la base %s", backup_file, dbname)
    cmd_restore = [
        "bash",
        "-lc",
        (
            f"PGPASSWORD='{password}' pg_restore -h {host} -p {port} -U {user} "
            f"-d {dbname} --clean --if-exists \"{backup_file}\""
        ),
    ]
    run_subprocess(cmd_restore)
    logger.info("Restauration PostgreSQL terminée")


def main() -> None:
    parser = argparse.ArgumentParser(description="Restauration PRA PostgreSQL")
    parser.add_argument(
        "--backup-dir",
        type=str,
        required=True,
        help="Répertoire contenant les dumps PostgreSQL",
    )
    parser.add_argument(
        "--no-drop",
        action="store_true",
        help="Ne pas supprimer/recréer la base avant restauration",
    )
    args = parser.parse_args()

    backup_dir = Path(args.backup_dir)
    if not backup_dir.is_dir():
        raise SystemExit(f"Répertoire de backup introuvable: {backup_dir}")

    dumps = sorted(backup_dir.glob("mairie_full_*.dump"))
    if not dumps:
        raise SystemExit("Aucun dump PostgreSQL trouvé dans le répertoire de backup")

    latest = dumps[-1]
    logger.info("Dernier dump détecté: %s", latest)
    restore_postgres(latest, drop_before=not args.no_drop)


if __name__ == "__main__":
    main()
