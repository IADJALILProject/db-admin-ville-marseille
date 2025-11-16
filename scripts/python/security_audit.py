import csv
import logging
import time
from pathlib import Path
from typing import List

import psycopg2
import psycopg2.extras

from db_utils import BASE_DIR, pg_connection

logger = logging.getLogger("db_admin.security")


def run_sql_file(path: Path) -> List[dict]:
    sql = path.read_text(encoding="utf-8")
    with pg_connection(autocommit=True) as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute(sql)
            rows = cur.fetchall()
    return [dict(r) for r in rows]


def export_csv(path: Path, rows: List[dict]) -> None:
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
    audits_dir = BASE_DIR / "security" / "audits_sql"
    out_dir = BASE_DIR / "security" / "audit_results"
    out_dir.mkdir(parents=True, exist_ok=True)

    timestamp = time.strftime("%Y%m%d_%H%M%S")

    for script in ["check_public_schema.sql", "check_weak_passwords.sql", "check_orphan_users.sql", "check_excessive_privileges.sql"]:
        path = audits_dir / script
        if not path.exists():
            logger.warning("Script d'audit manquant: %s", path)
            continue
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
