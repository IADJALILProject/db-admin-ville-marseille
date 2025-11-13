# scripts/python/perf_metrics_collector.py

import csv
import logging
import time
from pathlib import Path

import psycopg2
import psycopg2.extras

from db_utils import BASE_DIR, pg_connection

logger = logging.getLogger("db_admin.perf")


def collect_table_sizes() -> list:
    rows = []
    with pg_connection(autocommit=True) as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute(
                """
                SELECT
                    now()::timestamp        AS snapshot_ts,
                    n.nspname               AS schema_name,
                    c.relname               AS table_name,
                    pg_total_relation_size(c.oid)        AS total_bytes,
                    pg_relation_size(c.oid)              AS table_bytes,
                    pg_indexes_size(c.oid)               AS index_bytes,
                    coalesce(s.n_live_tup, 0)            AS live_rows
                FROM pg_class c
                JOIN pg_namespace n ON n.oid = c.relnamespace
                LEFT JOIN pg_stat_user_tables s ON s.relid = c.oid
                WHERE c.relkind = 'r'
                  AND n.nspname IN ('metier', 'referentiel')
                ORDER BY total_bytes DESC
                """
            )
            for r in cur.fetchall():
                rows.append(dict(r))
    return rows


def write_csv(path: Path, rows: list) -> None:
    if not rows:
        return
    fieldnames = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    logger.info("Collecte des métriques de performance")
    out_dir = BASE_DIR / "monitoring" / "metrics"
    out_dir.mkdir(parents=True, exist_ok=True)
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    path = out_dir / f"table_sizes_{timestamp}.csv"
    rows = collect_table_sizes()
    write_csv(path, rows)
    logger.info("Métriques de performance écrites dans %s", path)


if __name__ == "__main__":
    main()
