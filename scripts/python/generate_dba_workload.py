import logging
import random
import time

from db_utils import get_pg_connection

logger = logging.getLogger("db_admin.dba_workload")


def run_workload(iterations: int = 50, sleep_seconds: float = 0.1) -> None:
    """
    Génère une petite charge synthétique pour alimenter pg_stat_statements :
    - requêtes sur pg_stat_database, pg_class, pg_stat_all_tables, etc.
    - éventuellement un ANALYZE sur quelques tables utilisateur si dispo.
    """
    conn = get_pg_connection()
    conn.autocommit = True
    cur = conn.cursor()

    logger.info("Démarrage de la charge synthétique DBA (iterations=%s)", iterations)

    for i in range(iterations):
        # 1) Stats générales base
        cur.execute(
            """
            SELECT datname, numbackends, xact_commit, xact_rollback
            FROM pg_stat_database
            WHERE datname = current_database();
            """
        )

        # 2) Tirage aléatoire de quelques tables
        cur.execute(
            """
            SELECT n.nspname, c.relname
            FROM pg_class c
            JOIN pg_namespace n ON n.oid = c.relnamespace
            WHERE c.relkind = 'r'
              AND n.nspname NOT IN ('pg_catalog', 'information_schema')
            ORDER BY random()
            LIMIT 5;
            """
        )
        tables = cur.fetchall()

        # 3) Pour chaque table trouvée, on fait un petit SELECT
        for schema, table in tables:
            query = f"SELECT count(*) FROM {schema}.{table};"
            try:
                cur.execute(query)
            except Exception as e:
                logger.debug("Impossible d'exécuter %s : %s", query, e)

        # 4) Quelques requêtes sur pg_stat_all_tables pour les dashboards maintenance
        cur.execute(
            """
            SELECT schemaname, relname, n_live_tup, n_dead_tup
            FROM pg_stat_all_tables
            WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
            ORDER BY n_dead_tup DESC
            LIMIT 10;
            """
        )

        # 5) De temps en temps, un ANALYZE sur une table au hasard
        if i % 10 == 0 and tables:
            schema, table = random.choice(tables)
            analyze_query = f"ANALYZE {schema}.{table};"
            try:
                cur.execute(analyze_query)
            except Exception as e:
                logger.debug("Impossible d'exécuter %s : %s", analyze_query, e)

        time.sleep(sleep_seconds)

    logger.info("Fin de la charge synthétique DBA.")
    cur.close()
    conn.close()


def main():
    run_workload()


if __name__ == "__main__":
    main()
