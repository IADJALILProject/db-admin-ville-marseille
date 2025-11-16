import logging
import logging.config
import subprocess
import time
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

import psycopg2
import psycopg2.extras
import yaml
import os




BASE_DIR = Path(__file__).resolve().parents[2]
CONFIG_DIR = BASE_DIR / "config"
LOG_CONFIG_FILE = CONFIG_DIR / "logging.yml"

logger = logging.getLogger("db_admin")


def _setup_logging() -> None:
    if logger.handlers:
        return
    if LOG_CONFIG_FILE.exists():
        with LOG_CONFIG_FILE.open("r", encoding="utf-8") as f:
            cfg = yaml.safe_load(f)
        logging.config.dictConfig(cfg)
    else:
        logging.basicConfig(level=logging.INFO)


_setup_logging()


def load_yaml(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_config_global() -> Dict[str, Any]:
    return load_yaml(CONFIG_DIR / "config_global.yml")


def load_config_postgres() -> Dict[str, Any]:
    return load_yaml(CONFIG_DIR / "config_postgres.yml")


def load_config_mysql() -> Dict[str, Any]:
    return load_yaml(CONFIG_DIR / "config_mysql.yml")


def load_config_mssql() -> Dict[str, Any]:
    return load_yaml(CONFIG_DIR / "config_mssql.yml")


@dataclass
class DbConnectionInfo:
    host: str
    port: int
    database: str
    user: str
    password: str
    driver: Optional[str] = None


def get_postgres_conn_info() -> DbConnectionInfo:
    cfg = load_config_postgres()["connection"]
    return DbConnectionInfo(
        host=cfg["host"],
        port=int(cfg["port"]),
        database=cfg["database"],
        user=cfg["user"],
        password=cfg["password"],
    )


@contextmanager
def pg_connection(autocommit: bool = False):
    info = get_postgres_conn_info()
    conn = psycopg2.connect(
        host=info.host,
        port=info.port,
        dbname=info.database,
        user=info.user,
        password=info.password,
    )
    conn.autocommit = autocommit
    try:
        yield conn
    finally:
        conn.close()


def execute_sql_file_postgres(path: Path, autocommit: bool = True) -> None:
    logger.info("Exécution SQL Postgres: %s", path)
    sql = path.read_text(encoding="utf-8")
    with pg_connection(autocommit=autocommit) as conn:
        with conn.cursor() as cur:
            cur.execute(sql)


def run_subprocess(cmd: str, timeout: Optional[int] = None) -> subprocess.CompletedProcess:
    logger.info("Exécution commande: %s", cmd)
    started = time.time()
    result = subprocess.run(
        cmd,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=timeout,
    )
    duration = time.time() - started
    if result.returncode != 0:
        logger.error("Commande en erreur (%s s): %s\n%s", round(duration, 2), cmd, result.stderr.strip())
        raise RuntimeError(f"Echec commande {cmd}: {result.stderr}")
    logger.info("Commande terminée (%s s): %s", round(duration, 2), cmd)
    return result

def get_pg_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME", "mairie"),
        user=os.getenv("DB_USER", "db_admin"),
        password=os.getenv("DB_PASSWORD", "CHANGE_ME"),
    )