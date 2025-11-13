# scripts/python/manage_schemas.py

import logging
from pathlib import Path

from db_utils import BASE_DIR, execute_sql_file_postgres

logger = logging.getLogger("db_admin.manage_schemas")


DDL_ORDER = [
    "01_create_schema_referentiel.sql",
    "02_create_schema_metier.sql",
    "03_create_tables_referentiel.sql",
    "04_create_tables_citoyens_rdv.sql",
    "05_indexes_constraints.sql",
    "06_views_reporting.sql",
    "07_functions_rdv.sql"
]

DML_ORDER = [
    "10_seed_referentiel.sql",
    "11_insert_demo_from_csv.sql",
    "12_reseed_sequences.sql"
]


def apply_postgres_schemas() -> None:
    ddl_dir = BASE_DIR / "db" / "postgres" / "ddl"
    dml_dir = BASE_DIR / "db" / "postgres" / "dml"

    for fname in DDL_ORDER:
        path = ddl_dir / fname
        if path.exists():
            execute_sql_file_postgres(path)
        else:
            logger.warning("Fichier DDL manquant: %s", path)

    for fname in DML_ORDER:
        path = dml_dir / fname
        if path.exists():
            execute_sql_file_postgres(path)
        else:
            logger.warning("Fichier DML manquant: %s", path)


def main() -> None:
    logger.info("Déploiement des schémas PostgreSQL")
    apply_postgres_schemas()
    logger.info("Déploiement terminé")


if __name__ == "__main__":
    main()
