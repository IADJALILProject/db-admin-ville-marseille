from __future__ import annotations

from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator

from dbm_observability_utils import run_dbm_script, aggregate_status_files


DEFAULT_ARGS = {
    "owner": "db_admin",
    "depends_on_past": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
    "email_on_failure": True,
    "email": ["dba@mairie.fr"],
}

with DAG(
    dag_id="dbm_platform_observability",
    description="DAG global d'observabilité et d'administration pour la base 'mairie' (Ville de Marseille)",
    start_date=datetime(2025, 1, 1),
    schedule_interval="0 2 * * *",
    catchup=False,
    max_active_runs=1,
    default_args=DEFAULT_ARGS,
    tags=["db-admin", "postgres", "observability", "monitoring"],
) as dag:

    manage_schemas = PythonOperator(
        task_id="manage_schemas",
        python_callable=run_dbm_script,
        op_kwargs={
            "script_name": "manage_schemas.py",
            "task_label": "manage_schemas",
        },
        doc_md="""
        #### Gestion des schémas

        Crée et initialise les schémas DDL/DML de la base `mairie` :
        - Schémas: referentiel, metier
        - Tables, indexes, contraintes
        - Vues et fonctions PL/pgSQL
        - Données de seed
        """,
    )

    health_checks = PythonOperator(
        task_id="health_checks_pre",
        python_callable=run_dbm_script,
        op_kwargs={
            "script_name": "health_checks.py",
            "extra_args": ["--phase", "pre"],
            "task_label": "health_checks_pre",
        },
        doc_md="""
        #### Health checks préalables

        Vérifie l'état de santé de la base Postgres `mairie` avant les opérations
        sensibles (backup, métriques, audit, reporting).
        """,
    )

    run_backup = PythonOperator(
        task_id="run_backup",
        python_callable=run_dbm_script,
        op_kwargs={
            "script_name": "backup_runner.py",
            "task_label": "backup_runner",
        },
        doc_md="""
        #### Sauvegarde quotidienne

        Lance `backup_runner.py` pour réaliser le backup logique de la base `mairie`
        et l'écrire dans le répertoire de sauvegarde du projet.
        """,
    )

    collect_perf_metrics = PythonOperator(
        task_id="collect_perf_metrics",
        python_callable=run_dbm_script,
        op_kwargs={
            "script_name": "perf_metrics_collector.py",
            "task_label": "perf_metrics_collector",
        },
        doc_md="""
        #### Collecte des métriques de performance

        Collecte des indicateurs de performance (taille des tables, index, séquences,
        temps de requêtes, etc.) afin d'alimenter la couche Grafana/Prometheus.
        """,
    )

    run_security_audit = PythonOperator(
        task_id="run_security_audit",
        python_callable=run_dbm_script,
        op_kwargs={
            "script_name": "security_audit.py",
            "task_label": "security_audit",
        },
        doc_md="""
        #### Audit de sécurité

        Vérifie la configuration des rôles, privilèges et droits sur les schémas
        `metier` et `referentiel` pour la base `mairie`.
        """,
    )

    generate_reports = PythonOperator(
        task_id="generate_reports",
        python_callable=run_dbm_script,
        op_kwargs={
            "script_name": "generate_reports.py",
            "task_label": "generate_reports",
        },
        doc_md="""
        #### Rapports d'exploitation

        Génère des rapports (CSV/HTML/PDF) à partir des vues de reporting,
        stockés dans `data/monitoring/reports/` pour la DSI.
        """,
    )

    aggregate_status = PythonOperator(
        task_id="aggregate_status",
        python_callable=aggregate_status_files,
        doc_md="""
        #### Agrégation des statuts d'observabilité

        Regroupe tous les JSON de status produits par les tâches précédentes
        en un snapshot global `platform_observability_snapshot.json`,
        qui pourra être consommé par un dashboard Grafana (via une API / exporter).
        """,
    )

    manage_schemas >> health_checks >> run_backup >> collect_perf_metrics >> run_security_audit >> generate_reports >> aggregate_status
