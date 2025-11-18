"""
Health checks PostgreSQL pour la base 'mairie'.

- Vérifie que la base est joignable
- Compte les sessions actives / en attente / bloquantes
- Mesure la taille de la base
- Essaie d'estimer un temps moyen de requête (si statistiques disponibles)
- Insère une ligne dans monitoring.db_health_status
"""

import logging
import os
from datetime import datetime
from pathlib import Path

import psycopg2
from psycopg2 import sql  

from db_utils import get_pg_connection

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] health_checks: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    ch.setFormatter(formatter)
    logger.addHandler(ch)


MONITORING_ROOT = Path(os.getenv("DBM_MONITORING_DIR", "/opt/airflow/monitoring"))
REPORTS_DIR = MONITORING_ROOT / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)


def collect_health_metrics(conn) -> dict:
    """
    Collecte les métriques principales depuis Postgres.
    Retourne un dict prêt à être inséré dans monitoring.db_health_status.
    """
    metrics = {
        "is_up": False,
        "active_sessions": None,
        "waiting_sessions": None,
        "blocking_sessions": None,
        "avg_query_ms": None,
        "db_size_bytes": None,
    }

    with conn.cursor() as cur:
        try:
            cur.execute("SELECT 1;")
            cur.fetchone()
            metrics["is_up"] = True
        except psycopg2.Error as e:
            logger.error("Échec du check 'SELECT 1': %s", e)
            metrics["is_up"] = False
            return metrics

        try:
            cur.execute(
                """
                SELECT
                  count(*) FILTER (WHERE state = 'active')       AS active_sessions,
                  count(*) FILTER (WHERE wait_event IS NOT NULL) AS waiting_sessions
                FROM pg_stat_activity
                WHERE datname = current_database();
                """
            )
            row = cur.fetchone()
            metrics["active_sessions"] = row[0]
            metrics["waiting_sessions"] = row[1]
        except psycopg2.Error as e:
            logger.warning("Impossible de lire pg_stat_activity: %s", e)

        try:
            cur.execute(
                """
                SELECT count(*)
                FROM pg_locks l
                JOIN pg_stat_activity a ON l.pid = a.pid
                WHERE NOT l.granted;
                """
            )
            metrics["blocking_sessions"] = cur.fetchone()[0]
        except psycopg2.Error as e:
            logger.warning("Impossible de lire pg_locks/pg_stat_activity: %s", e)

        try:
            cur.execute("SELECT pg_database_size(current_database());")
            metrics["db_size_bytes"] = cur.fetchone()[0]
        except psycopg2.Error as e:
            logger.warning("Impossible de lire pg_database_size: %s", e)

        try:
            cur.execute(
                """
                SELECT
                  CASE
                    WHEN sum(xact_commit + xact_rollback) = 0 THEN NULL
                    ELSE sum(blks_read_time + blks_write_time)
                         / sum(xact_commit + xact_rollback)
                  END AS avg_ms
                FROM pg_stat_database
                WHERE datname = current_database();
                """
            )
            val = cur.fetchone()[0]
            metrics["avg_query_ms"] = float(val) if val is not None else None
        except psycopg2.Error as e:
            logger.warning("Impossible d'estimer avg_query_ms: %s", e)

    return metrics


def insert_health_row(conn, metrics: dict) -> None:
    """
    Insère une ligne dans monitoring.db_health_status.
    """
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO monitoring.db_health_status
              (is_up, active_sessions, avg_query_ms, db_size_bytes,
               waiting_sessions, blocking_sessions)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                metrics["is_up"],
                metrics["active_sessions"],
                metrics["avg_query_ms"],
                metrics["db_size_bytes"],
                metrics["waiting_sessions"],
                metrics["blocking_sessions"],
            ),
        )


def write_markdown_report(metrics: dict) -> None:
    """
    Écrit un petit rapport Markdown dans monitoring/reports/rapport_health_status.md.
    """
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    md_path = REPORTS_DIR / "rapport_health_status.md"

    lines = [
        f"# Health check PostgreSQL – {ts}",
        "",
        f"- **Instance up** : {' OUI' if metrics['is_up'] else ' NON'}",
        f"- **Sessions actives** : {metrics['active_sessions']}",
        f"- **Sessions en attente** : {metrics['waiting_sessions']}",
        f"- **Sessions bloquantes** : {metrics['blocking_sessions']}",
        f"- **Taille base** : {metrics['db_size_bytes']} octets",
        f"- **Temps moyen requêtes (approx)** : {metrics['avg_query_ms']} ms",
        "",
    ]

    md_path.write_text("\n".join(lines), encoding="utf-8")
    logger.info("Rapport Markdown écrit dans %s", md_path)


def main() -> None:
    logger.info("Démarrage des health checks PostgreSQL...")
    conn = get_pg_connection()
    conn.autocommit = True

    try:
        metrics = collect_health_metrics(conn)
        logger.info("Métriques collectées: %s", metrics)

        insert_health_row(conn, metrics)
        logger.info("Ligne insérée dans monitoring.db_health_status")

        write_markdown_report(metrics)
    finally:
        conn.close()
        logger.info("Connexion PostgreSQL fermée.")

    logger.info("Health checks terminés avec succès.")


if __name__ == "__main__":
    main()
