import csv
import logging
import time
from pathlib import Path
from typing import List, Dict

import psycopg2
import psycopg2.extras

from db_utils import BASE_DIR, get_pg_connection

logger = logging.getLogger("db_admin.security")
logger.setLevel(logging.INFO)

if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] security_audit: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    ch.setFormatter(formatter)
    logger.addHandler(ch)


def run_sql_file(path: Path) -> List[Dict]:
    """
    Exécute un fichier SQL et retourne les résultats sous forme de liste de dict.
    """
    sql = path.read_text(encoding="utf-8")

    conn = get_pg_connection()
    conn.autocommit = True

    try:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute(sql)
            rows = cur.fetchall()
            return [dict(r) for r in rows]
    finally:
        conn.close()


def export_csv(path: Path, rows: List[Dict]) -> None:
    """
    Exporte les lignes dans un CSV (un fichier par script d’audit).
    """
    if not rows:
        return

    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(rows[0].keys())

    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    logger.info("Exécution des audits de sécurité")

    # Les scripts SQL restent dans le repo (lecture seule)
    audits_dir = BASE_DIR / "security" / "audits_sql"

    # Les résultats sont écrits dans un répertoire Airflow (écriture OK)
    monitoring_base = Path("/opt/airflow/monitoring")
    out_dir = monitoring_base / "security" / "audit_results"
    out_dir.mkdir(parents=True, exist_ok=True)

    timestamp = time.strftime("%Y%m%d_%H%M%S")

    scripts = [
        "check_public_schema.sql",
        "check_weak_passwords.sql",
        "check_orphan_users.sql",
        "check_excessive_privileges.sql",
    ]

    for script in scripts:
        path = audits_dir / script
        if not path.exists():
            logger.warning("Script d'audit manquant: %s", path)
            continue

        logger.info("Exécution de l'audit: %s", script)
        rows = run_sql_file(path)

        if rows:
            out_csv = out_dir / f"{script.replace('.sql', '')}_{timestamp}.csv"
            export_csv(out_csv, rows)
            logger.info("Rapport d'audit généré: %s", out_csv)
        else:
            logger.info("Aucune anomalie détectée pour %s", script)

    logger.info("Audits de sécurité terminés")


if __name__ == "__main__":
    main()
