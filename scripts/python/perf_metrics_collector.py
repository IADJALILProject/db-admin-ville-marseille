"""
Collecte des métriques de performance sur les tables PostgreSQL :

- Récupère la taille totale de chaque table (pg_total_relation_size)
- Insère les lignes dans monitoring.table_sizes
- Écrit un CSV dans monitoring/metrics/table_sizes_YYYYMMDD_HHMMSS.csv

- Récupère des métriques WAL (journal de transactions) dans monitoring.wal_activity
- Récupère les locks non accordés dans monitoring.lock_events
- Récupère un indicateur simple de bloat (lignes mortes) dans monitoring.table_bloat
"""

import csv
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Tuple, Optional, Any

from db_utils import get_pg_connection

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] perf_metrics: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    ch.setFormatter(formatter)
    logger.addHandler(ch)


PROJECT_ROOT = Path(__file__).resolve().parents[3]
MONITORING_DIR = Path(os.getenv("DBM_MONITORING_DIR", "/opt/airflow/monitoring"))
METRICS_DIR = MONITORING_DIR / "metrics"
METRICS_DIR.mkdir(parents=True, exist_ok=True)

def fetch_table_sizes(conn) -> List[Tuple[str, str, int]]:
    """
    Retourne une liste de tuples (schema_name, table_name, size_bytes).
    """
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT
              n.nspname  AS schema_name,
              c.relname  AS table_name,
              pg_total_relation_size(c.oid) AS size_bytes
            FROM pg_class c
            JOIN pg_namespace n ON n.oid = c.relnamespace
            WHERE c.relkind = 'r'
              AND n.nspname NOT IN ('pg_catalog', 'information_schema')
            ORDER BY size_bytes DESC;
            """
        )
        rows = cur.fetchall()

    return rows


def insert_table_sizes(conn, rows: List[Tuple[str, str, int]]) -> None:
    """
    Insère les tailles de tables dans monitoring.table_sizes.
    """
    with conn.cursor() as cur:
        for schema_name, table_name, size_bytes in rows:
            cur.execute(
                """
                INSERT INTO monitoring.table_sizes (schema_name, table_name, size_bytes)
                VALUES (%s, %s, %s)
                """,
                (schema_name, table_name, size_bytes),
            )


def write_csv(rows: List[Tuple[str, str, int]]) -> Path:
    """
    Écrit un CSV avec les tailles de table dans monitoring/metrics/...
    Retourne le chemin du fichier.
    """
    ts_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_path = METRICS_DIR / f"table_sizes_{ts_str}.csv"

    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["schema_name", "table_name", "size_bytes"])
        for schema_name, table_name, size_bytes in rows:
            writer.writerow([schema_name, table_name, size_bytes])

    return csv_path

def fetch_wal_activity(conn) -> Optional[Tuple[Any, Any, int]]:
    """
    Retourne un tuple (wal_lsn, wal_bytes_total, wal_segment_size).
    """
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT
              pg_current_wal_lsn() AS wal_lsn,
              pg_wal_lsn_diff(pg_current_wal_lsn(), '0/0') AS wal_bytes_total,
              current_setting('wal_segment_size')::int AS wal_segment_size;
            """
        )
        row = cur.fetchone()
    return row


def insert_wal_activity(conn, wal_lsn, wal_bytes_total, wal_segment_size, notes: str = "") -> None:
    """
    Insère un snapshot de WAL dans monitoring.wal_activity.
    """
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO monitoring.wal_activity
              (wal_lsn, wal_bytes_total, wal_segment_size, notes)
            VALUES (%s, %s, %s, %s)
            """,
            (wal_lsn, wal_bytes_total, wal_segment_size, notes),
        )


def fetch_lock_events(conn) -> List[Tuple[int, str, str, str, bool, Optional[str]]]:
    """
    Retourne les locks non accordés (NOT granted) avec la requête associée.
    """
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT
              l.pid,
              l.locktype,
              CASE
                WHEN l.relation IS NOT NULL THEN
                  pg_catalog.format('%s.%s', n.nspname, c.relname)
                ELSE
                  NULL
              END AS relation,
              l.mode,
              l.granted,
              a.query
            FROM pg_locks l
            LEFT JOIN pg_class c ON l.relation = c.oid
            LEFT JOIN pg_namespace n ON c.relnamespace = n.oid
            LEFT JOIN pg_stat_activity a ON l.pid = a.pid
            WHERE NOT l.granted;
            """
        )
        rows = cur.fetchall()
    return rows


def insert_lock_events(conn, rows: List[Tuple[int, str, str, str, bool, Optional[str]]]) -> None:
    """
    Insère les locks non accordés dans monitoring.lock_events.
    """
    if not rows:
        return

    with conn.cursor() as cur:
        for pid, locktype, relation, mode, granted, query in rows:
            cur.execute(
                """
                INSERT INTO monitoring.lock_events
                  (pid, locktype, relation, mode, granted, query)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (pid, locktype, relation, mode, granted, query),
            )


def fetch_table_bloat(conn) -> List[Tuple[str, str, int, int, float]]:
    """
    Retourne un indicateur simple de bloat par table (dead rows / total rows).

    On se base sur pg_stat_all_tables pour les schémas métier.
    """
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT
              schemaname,
              relname,
              n_live_tup AS est_rows,
              n_dead_tup AS dead_rows,
              CASE
                WHEN n_live_tup + n_dead_tup = 0 THEN 0
                ELSE 100.0 * n_dead_tup / (n_live_tup + n_dead_tup)
              END AS dead_pct
            FROM pg_stat_all_tables
            WHERE schemaname IN ('metier', 'referentiel');
            """
        )
        rows = cur.fetchall()
    return rows


def insert_table_bloat(conn, rows: List[Tuple[str, str, int, int, float]]) -> None:
    """
    Insère l'indicateur de bloat dans monitoring.table_bloat.
    """
    if not rows:
        return

    with conn.cursor() as cur:
        for schema_name, table_name, est_rows, dead_rows, dead_pct in rows:
            cur.execute(
                """
                INSERT INTO monitoring.table_bloat
                  (schema_name, table_name, est_rows, dead_rows, dead_pct)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (schema_name, table_name, est_rows, dead_rows, dead_pct),
            )

def main() -> None:
    logger.info("Démarrage de la collecte des métriques de performance (tailles des tables, WAL, locks, bloat)...")
    conn = get_pg_connection()
    conn.autocommit = True

    try:
        rows = fetch_table_sizes(conn)
        logger.info("Tailles récupérées pour %d tables.", len(rows))

        insert_table_sizes(conn, rows)
        logger.info("Tailles insérées dans monitoring.table_sizes")

        csv_path = write_csv(rows)
        logger.info("CSV écrit dans %s", csv_path)

        wal_row = fetch_wal_activity(conn)
        if wal_row:
            wal_lsn, wal_bytes_total, wal_segment_size = wal_row
            insert_wal_activity(conn, wal_lsn, wal_bytes_total, wal_segment_size, notes="snapshot perf_metrics_collector")
            logger.info(
                "WAL activity insérée (lsn=%s, wal_bytes_total=%s, segment_size=%s)",
                wal_lsn,
                wal_bytes_total,
                wal_segment_size,
            )
        else:
            logger.warning("Impossible de récupérer la WAL activity.")

        lock_rows = fetch_lock_events(conn)
        logger.info("Locks non accordés récupérés: %d", len(lock_rows))
        insert_lock_events(conn, lock_rows)

        bloat_rows = fetch_table_bloat(conn)
        logger.info("Bloat récupéré pour %d tables.", len(bloat_rows))
        insert_table_bloat(conn, bloat_rows)

    finally:
        conn.close()
        logger.info("Connexion PostgreSQL fermée.")

    logger.info("Collecte des métriques de performance terminée.")


if __name__ == "__main__":
    main()
