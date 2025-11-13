-- security/audits_sql/check_public_schema.sql
-- Rapporte les objets (tables / vues) sur lesquels le rôle PUBLIC
-- a des privilèges, à partir de information_schema.table_privileges.

SET search_path TO public;

WITH public_privs AS (
    SELECT
        current_database()        AS database_name,
        table_schema,
        table_name,
        privilege_type
    FROM information_schema.table_privileges
    WHERE grantee = 'PUBLIC'
      AND table_schema NOT IN ('pg_catalog', 'information_schema')
),
agg AS (
    SELECT
        database_name,
        table_schema,
        table_name,
        string_agg(privilege_type, ',') AS privileges
    FROM public_privs
    GROUP BY database_name, table_schema, table_name
)
SELECT
    database_name,
    table_schema,
    table_name,
    privileges,
    'EXPOSED_TO_PUBLIC' AS status,
    'Vérifier si l''exposition au rôle PUBLIC est justifiée.' AS recommendation
FROM agg
ORDER BY table_schema, table_name;
