import logging
from pathlib import Path

from db_utils import BASE_DIR, get_pg_connection

logger = logging.getLogger("db_admin.manage_schemas")

DDL_ORDER = [
    "01_create_schema_referentiel.sql",
    "02_create_schema_metier.sql",
    "03_create_tables_referentiel.sql",
    "04_create_tables_citoyens_rdv.sql",
    "05_indexes_constraints.sql",
    "06_views_reporting.sql",
    "07_functions_rdv.sql",
    "08_monitoring_schema.sql",
    "09_dba_performance_views.sql"
]

DML_ORDER = [
    "10_seed_referentiel.sql",
    "11_insert_demo_from_csv.sql",
    "12_reseed_sequences.sql",
]


def _execute_sql_file(path: Path, conn) -> None:
    logger.info("Exécution SQL: %s", path)
    sql = path.read_text(encoding="utf-8")
    with conn.cursor() as cur:
        cur.execute(sql)
    conn.commit()


def apply_postgres_schemas() -> None:
    ddl_dir = BASE_DIR / "db" / "postgres" / "ddl"
    dml_dir = BASE_DIR / "db" / "postgres" / "dml"

    with get_pg_connection() as conn:
        # DDL
        for filename in DDL_ORDER:
            path = ddl_dir / filename
            if path.exists():
                _execute_sql_file(path, conn)
            else:
                logger.warning("Fichier DDL manquant: %s", path)

        # DML
        for filename in DML_ORDER:
            path = dml_dir / filename
            if path.exists():
                _execute_sql_file(path, conn)
            else:
                logger.warning("Fichier DML manquant: %s", path)


def main() -> None:
    logger.info("Déploiement des schémas PostgreSQL")
    apply_postgres_schemas()
    logger.info("Déploiement terminé")


if __name__ == "__main__":
    main()
