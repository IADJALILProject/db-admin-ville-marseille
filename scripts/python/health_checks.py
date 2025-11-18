"""
Health checks PostgreSQL pour la base 'mairie'.

- Vérifie la disponibilité
- Force une requête synthétique pour alimenter les statistiques
- Mesure sessions actives, attentes, locks
- Mesure la taille de la base
- Estime un temps moyen de requête
- Insère dans monitoring.db_health_status
"""

import logging
import os
from datetime import datetime
from pathlib import Path

import psycopg2
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


def force_synthetic_query(cur):
    """
    Exécute une requête simple mais mesurable
    pour forcer l'alimentation de pg_stat_database.
    """
    try:
        cur.execute("""
            SELECT
                sum generate_series(1, 50000)
            FROM generate_series(1, 50)
        """)
        cur.fetchone()
        logger.info("Requête synthétique exécutée pour alimenter les stats.")
    except psycopg2.Error as e:
        logger.warning("Impossible d'exécuter la requête synthétique : %s", e)


def collect_health_metrics(conn) -> dict:
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
            logger.error("SELECT 1 failed: %s", e)
            return metrics

        force_synthetic_query(cur)

        try:
            cur.execute("""
                SELECT
                  count(*) FILTER (WHERE state = 'active'),
                  count(*) FILTER (WHERE wait_event IS NOT NULL)
                FROM pg_stat_activity
                WHERE datname = current_database();
            """)
            row = cur.fetchone()
            metrics["active_sessions"] = row[0]
            metrics["waiting_sessions"] = row[1]
        except psycopg2.Error as e:
            logger.warning("pg_stat_activity error: %s", e)

        try:
            cur.execute("""
                SELECT count(*)
                FROM pg_locks l
                JOIN pg_stat_activity a ON l.pid = a.pid
                WHERE NOT l.granted;
            """)
            metrics["blocking_sessions"] = cur.fetchone()[0]
        except psycopg2.Error as e:
            logger.warning("pg_locks error: %s", e)

        try:
            cur.execute("SELECT pg_database_size(current_database());")
            metrics["db_size_bytes"] = cur.fetchone()[0]
        except psycopg2.Error as e:
            logger.warning("pg_database_size error: %s", e)

        try:
            cur.execute("""
                SELECT
                  CASE
                    WHEN sum(xact_commit + xact_rollback) = 0 THEN NULL
                    ELSE sum(blk_read_time + blk_write_time)
                         / sum(xact_commit + xact_rollback)
                  END AS avg_ms
                FROM pg_stat_database
                WHERE datname = current_database();
            """)
            val = cur.fetchone()[0]
            metrics["avg_query_ms"] = float(val) if val is not None else 0.0
        except psycopg2.Error as e:
            logger.warning("avg_query_ms error: %s", e)

    return metrics


def insert_health_row(conn, metrics: dict) -> None:
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO monitoring.db_health_status
              (is_up, active_sessions, avg_query_ms, db_size_bytes,
               waiting_sessions, blocking_sessions)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            metrics["is_up"],
            metrics["active_sessions"],
            metrics["avg_query_ms"],
            metrics["db_size_bytes"],
            metrics["waiting_sessions"],
            metrics["blocking_sessions"],
        ))


def write_markdown_report(metrics: dict) -> None:
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    md_path = REPORTS_DIR / "rapport_health_status.md"

    lines = [
        f"# Health check PostgreSQL – {ts}",
        "",
        f"- **Instance up** : {'OUI' if metrics['is_up'] else 'NON'}",
        f"- **Sessions actives** : {metrics['active_sessions']}",
        f"- **Sessions en attente** : {metrics['waiting_sessions']}",
        f"- **Sessions bloquantes** : {metrics['blocking_sessions']}",
        f"- **Taille base** : {metrics['db_size_bytes']} octets",
        f"- **Temps moyen (ms)** : {metrics['avg_query_ms']} ms",
    ]

    md_path.write_text("\n".join(lines), encoding="utf-8")
    logger.info("Rapport Markdown écrit.")


def main() -> None:
    logger.info("Démarrage health checks PostgreSQL...")
    conn = get_pg_connection()
    conn.autocommit = True

    try:
        metrics = collect_health_metrics(conn)
        logger.info("Métriques collectées: %s", metrics)

        insert_health_row(conn, metrics)
        logger.info("Insertion OK")

        write_markdown_report(metrics)
    finally:
        conn.close()
        logger.info("Connexion fermée")


if __name__ == "__main__":
    main()
