# scripts/python/health_checks.py

import json
import logging
import time
from pathlib import Path
from typing import Dict, Any
import os
import psycopg2
import psycopg2.extras

from db_utils import BASE_DIR, get_postgres_conn_info, pg_connection

logger = logging.getLogger("db_admin.health")


def check_postgres_connectivity() -> Dict[str, Any]:
    info = get_postgres_conn_info()
    started = time.time()
    ok = False
    error = ""
    try:
        with pg_connection(autocommit=True) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                cur.fetchone()
        ok = True
    except Exception as exc:
        error = str(exc)
        logger.exception("Erreur de connectivité Postgres")
    latency_ms = round((time.time() - started) * 1000, 2)
    return {
        "engine": "postgres",
        "host": info.host,
        "port": info.port,
        "database": info.database,
        "ok": ok,
        "latency_ms": latency_ms,
        "error": error,
    }


def postgres_basic_metrics() -> Dict[str, Any]:
    metrics: Dict[str, Any] = {}
    with pg_connection(autocommit=True) as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute("SELECT count(*) AS sessions FROM pg_stat_activity;")
            metrics["sessions_total"] = cur.fetchone()["sessions"]

            cur.execute(
                "SELECT sum(pg_database_size(datname)) AS total_db_size "
                "FROM pg_database WHERE datistemplate = false;"
            )
            metrics["total_db_size_bytes"] = cur.fetchone()["total_db_size"]

            cur.execute(
                "SELECT count(*) AS locks_count "
                "FROM pg_locks l JOIN pg_database d ON l.database = d.oid "
                "WHERE d.datname = current_database();"
            )
            metrics["locks_count"] = cur.fetchone()["locks_count"]
    return metrics


def write_health_status(payload):
    from decimal import Decimal
    def convert_decimal(obj):
        if isinstance(obj, Decimal):
            return float(obj)
        if isinstance(obj, dict):
            return {k: convert_decimal(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [convert_decimal(v) for v in obj]
        return obj

    payload = convert_decimal(payload)

    os.makedirs("monitoring/status", exist_ok=True)
    with open("monitoring/status/health_status.json", "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)

def main() -> None:
    logger.info("Exécution des health checks")
    status = check_postgres_connectivity()
    metrics = postgres_basic_metrics()
    payload = {"status": status, "metrics": metrics, "timestamp": time.time()}
    write_health_status(payload)
    logger.info("Health checks terminés")


if __name__ == "__main__":
    main()
