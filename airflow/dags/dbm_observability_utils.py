from __future__ import annotations

import json
import os
import subprocess
from datetime import datetime
from pathlib import Path
from textwrap import indent
from typing import Any, Dict, List, Optional

import psycopg2
from airflow.exceptions import AirflowException
from airflow.utils.context import Context

# Racine du projet à l'intérieur du conteneur Airflow
PROJECT_ROOT = Path("/opt/db-admin-ville-marseille")
SCRIPTS_DIR = PROJECT_ROOT / "scripts" / "python"

# Racine du répertoire de monitoring (overridable par env)
MONITORING_ROOT = Path(
    os.getenv("DBM_MONITORING_DIR", "/opt/db-admin-ville-marseille/monitoring")
)
STATUS_DIR = MONITORING_ROOT / "status"
STATUS_DIR.mkdir(parents=True, exist_ok=True)

# Paramètres PostgreSQL utilisés pour stocker les statuts dans monitoring.task_status
PG_HOST = os.getenv("DBM_PG_HOST", "postgres")  # Docker service "postgres"
PG_PORT = int(os.getenv("DBM_PG_PORT", "5432"))
PG_DATABASE = os.getenv("DBM_PG_DATABASE", "mairie")
PG_USER = os.getenv("DBM_PG_USER", "db_admin")
PG_PASSWORD = os.getenv("DBM_PG_PASSWORD", "CHANGE_ME")


def _get_monitoring_pg_connection():
    """
    Connexion PostgreSQL pour la table monitoring.task_status.
    """
    return psycopg2.connect(
        host=PG_HOST,
        port=PG_PORT,
        dbname=PG_DATABASE,
        user=PG_USER,
        password=PG_PASSWORD,
    )


def _write_status_json(
    *,
    label: str,
    context: Context,
    status: str,
    details: Dict[str, Any],
    started_at: Optional[datetime] = None,
    finished_at: Optional[datetime] = None,
) -> None:
    """
    Écrit un fichier JSON de statut sur le disque et, si possible,
    insère une ligne dans monitoring.task_status (best effort).
    """
    ti = context["ti"]
    log = getattr(ti, "log", None)

    if started_at is None:
        started_at = getattr(ti, "start_date", None)
    if finished_at is None:
        finished_at = getattr(ti, "end_date", None)

    duration_seconds: Optional[float] = None
    if started_at and finished_at:
        duration_seconds = (finished_at - started_at).total_seconds()

    logical_dt = getattr(ti, "logical_date", None) or ti.execution_date

    payload = {
        "label": label,
        "status": status,
        "dag_id": ti.dag_id,
        "task_id": ti.task_id,
        "run_id": ti.run_id,
        "logical_date": logical_dt.isoformat(),
        "try_number": ti.try_number,
        "ts_utc": datetime.utcnow().isoformat(),
        "started_at": started_at.isoformat() if started_at else None,
        "finished_at": finished_at.isoformat() if finished_at else None,
        "duration_seconds": duration_seconds,
        "details": details,
    }

    # ---- 1) Écriture fichier JSON sur disque ----
    STATUS_DIR.mkdir(parents=True, exist_ok=True)
    status_file = STATUS_DIR / f"{ti.dag_id}__{ti.task_id}.json"
    with status_file.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    # ---- 2) Insertion en base dans monitoring.task_status (best effort) ----
    try:
        conn = _get_monitoring_pg_connection()
        conn.autocommit = True
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO monitoring.task_status
                  (dag_id, task_id, run_id, status, try_number,
                   started_at, finished_at, duration_seconds, details)
                VALUES (%s, %s, %s, %s, %s,
                        %s, %s, %s, %s::jsonb)
                """,
                (
                    ti.dag_id,
                    ti.task_id,
                    ti.run_id,
                    status,
                    ti.try_number,
                    started_at,
                    finished_at,
                    duration_seconds,
                    json.dumps(details),
                ),
            )
        conn.close()
    except Exception as exc:  # on ne fait pas échouer la task à cause du monitoring
        if log:
            log.warning(
                "[%s] Impossible d'insérer le statut dans monitoring.task_status : %s",
                label,
                exc,
            )
        else:
            print(
                f"[{label}] WARNING: impossible d'insérer le statut en base : {exc}"
            )


def aggregate_status_files(**context: Context) -> None:
    """
    Agrège tous les fichiers JSON de status en un snapshot global
    (platform_observability_snapshot.json).
    """
    ti = context["ti"]
    log = ti.log

    logical_dt = getattr(ti, "logical_date", None) or ti.execution_date

    log.info("[aggregate_status] Agrégation des fichiers JSON de status…")
    snapshot: Dict[str, Any] = {
        "dag_id": ti.dag_id,
        "run_id": ti.run_id,
        "logical_date": logical_dt.isoformat(),
        "tasks": {},
    }

    for json_path in STATUS_DIR.glob("*.json"):
        try:
            with json_path.open("r", encoding="utf-8") as f:
                data = json.load(f)
            task_id = data.get("task_id") or json_path.stem
            snapshot["tasks"][task_id] = data
        except Exception as exc:
            log.warning(
                "[aggregate_status] Impossible de lire %s : %s",
                json_path,
                exc,
            )

    snapshot_path = STATUS_DIR / "platform_observability_snapshot.json"
    with snapshot_path.open("w", encoding="utf-8") as f:
        json.dump(snapshot, f, ensure_ascii=False, indent=2)

    log.info(
        "[aggregate_status] Snapshot global écrit dans %s (tâches agrégées: %d)",
        snapshot_path,
        len(snapshot["tasks"]),
    )


def run_dbm_script(
    script_name: str,
    extra_args: Optional[List[str]] = None,
    task_label: Optional[str] = None,
    **context: Context,
) -> str:
    """
    Exécute un script Python du projet (scripts/python/...), capture stdout/stderr,
    écrit un statut détaillé, et remonte une AirflowException en cas d’échec.
    """
    ti = context["ti"]
    log = ti.log

    label = task_label or script_name
    script_path = SCRIPTS_DIR / script_name

    if not script_path.exists():
        now = datetime.utcnow()
        msg = f"[{label}] Script introuvable: {script_path}"
        log.error(msg)
        _write_status_json(
            label=label,
            context=context,
            status="error",
            details={"error": "script_not_found", "path": str(script_path)},
            started_at=now,
            finished_at=now,
        )
        raise AirflowException(msg)

    cmd = ["python", str(script_path)]
    if extra_args:
        cmd.extend(extra_args)

    logical_dt = getattr(ti, "logical_date", None) or ti.execution_date

    log.info(
        "[%s] Début d'exécution | dag_id=%s task_id=%s run_id=%s logical_date=%s",
        label,
        ti.dag_id,
        ti.task_id,
        ti.run_id,
        logical_dt,
    )
    log.info(" [%s] Commande exécutée: %s", label, " ".join(cmd))

    started_at = datetime.utcnow()

    try:
        result = subprocess.run(
            cmd,
            check=False,
            capture_output=True,
            text=True,
        )
        finished_at = datetime.utcnow()
    except Exception as exc:
        finished_at = datetime.utcnow()
        log.exception("[%s] Exception lors de l'exécution du script.", label)
        _write_status_json(
            label=label,
            context=context,
            status="error",
            details={"error": "exception", "exception": str(exc)},
            started_at=started_at,
            finished_at=finished_at,
        )
        raise AirflowException(f"[{label}] Échec d'exécution (exception)") from exc

    if result.stdout:
        log.info(
            " [%s] STDOUT:\n%s",
            label,
            indent(result.stdout.rstrip(), prefix="    "),
        )

    if result.stderr:
        log.warning(
            " [%s] STDERR:\n%s",
            label,
            indent(result.stderr.rstrip(), prefix="    "),
        )

    if result.returncode != 0:
        msg = f"[{label}] Script terminé avec un code de retour non nul: {result.returncode}"
        log.error(msg)
        _write_status_json(
            label=label,
            context=context,
            status="error",
            details={
                "error": "non_zero_return_code",
                "return_code": result.returncode,
            },
            started_at=started_at,
            finished_at=finished_at,
        )
        raise AirflowException(msg)

    log.info(" [%s] Script exécuté avec succès (rc=0).", label)
    _write_status_json(
        label=label,
        context=context,
        status="success",
        details={"return_code": result.returncode},
        started_at=started_at,
        finished_at=finished_at,
    )
    return result.stdout or ""
