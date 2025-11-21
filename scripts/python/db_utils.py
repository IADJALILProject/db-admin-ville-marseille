import logging
import logging.config
import os
import subprocess
import time
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional
import psycopg2
import psycopg2.extras
import yaml


BASE_DIR = Path(__file__).resolve().parents[2]
CONFIG_DIR = BASE_DIR / "config"
LOG_CONFIG_FILE = CONFIG_DIR / "logging.yml"

logger = logging.getLogger("db_admin")

def _setup_logging() -> None:
    """Initialise le logging à partir de logging.yml si présent."""
    if logger.handlers:
        return
    if LOG_CONFIG_FILE.exists():
        with LOG_CONFIG_FILE.open("r", encoding="utf-8") as f:
            cfg = yaml.safe_load(f) or {}

        handlers = cfg.get("handlers", {})
        for handler_cfg in handlers.values():
            filename = handler_cfg.get("filename")
            if filename:
                path = Path(filename)
                if not path.is_absolute():
                    path = BASE_DIR / path
                path.parent.mkdir(parents=True, exist_ok=True)
                handler_cfg["filename"] = str(path)

        logging.config.dictConfig(cfg)
    else:
        logging.basicConfig(level=logging.INFO)



def load_yaml(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_config_postgres() -> Dict[str, Any]:
    return load_yaml(CONFIG_DIR / "config_postgres.yml")


@dataclass
class DbConnectionInfo:
    host: str
    port: int
    database: str
    user: str
    password: str


def get_postgres_conn_info() -> DbConnectionInfo:
    """Connexion Postgres via fichier config_postgres.yml (usage host)."""
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
    """Context manager Postgres basé sur config_postgres.yml (usage host)."""
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
    """Exécute un fichier .sql sur Postgres (utilisé par manage_schemas.py)."""
    logger.info("Exécution SQL Postgres: %s", path)
    sql = path.read_text(encoding="utf-8")
    with pg_connection(autocommit=autocommit) as conn:
        with conn.cursor() as cur:
            cur.execute(sql)


def run_subprocess(cmd: str, timeout: Optional[int] = None) -> subprocess.CompletedProcess:
    """Helper générique pour lancer une commande shell avec logs."""
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
        logger.error(
            "Commande en erreur (%s s): %s\n%s",
            round(duration, 2),
            cmd,
            result.stderr.strip(),
        )
        raise RuntimeError(f"Echec commande {cmd}: {result.stderr}")
    logger.info("Commande terminée (%s s): %s", round(duration, 2), cmd)
    return result


# ---------------------------------------------------------------------------
# Connexion Postgres via variables d'environnement DBM_PG_*
# (usage : scripts exécutés dans le conteneur Airflow)
# ---------------------------------------------------------------------------

PG_ENV_HOST = os.getenv("DBM_PG_HOST", "postgres")
PG_ENV_PORT = int(os.getenv("DBM_PG_PORT", "5432"))
PG_ENV_DATABASE = os.getenv("DBM_PG_DATABASE", "mairie")
PG_ENV_USER = os.getenv("DBM_PG_USER", "db_admin")
PG_ENV_PASSWORD = os.getenv("DBM_PG_PASSWORD", "CHANGE_ME")


def get_pg_connection():
    """
    Connexion PostgreSQL basée sur les variables d'environnement DBM_PG_*.
    Utilisée par health_checks.py, perf_metrics.py, backups, etc.
    """
    return psycopg2.connect(
        host=PG_ENV_HOST,
        port=PG_ENV_PORT,
        dbname=PG_ENV_DATABASE,
        user=PG_ENV_USER,
        password=PG_ENV_PASSWORD,
    )

def load_config_global() -> Dict[str, Any]:
    """
    Charge la configuration globale depuis config/config_global.yml.
    Utilisé par les scripts comme backup_runner.py (répertoires, rétention, etc.).
    """
    path = CONFIG_DIR / "config_global.yml"
    if not path.exists():
        logger.warning("Fichier de configuration globale introuvable: %s", path)
        return {}
    return load_yaml(path)
