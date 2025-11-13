-- security/audits_sql/check_excessive_privileges.sql

SET search_path TO public;

WITH privileges AS (
    SELECT
        current_database()                         AS database_name,
        table_schema,
        table_name,
        grantee,
        string_agg(DISTINCT privilege_type, ',')   AS privileges
    FROM information_schema.table_privileges
    WHERE table_schema NOT IN ('pg_catalog', 'information_schema')
    GROUP BY database_name, table_schema, table_name, grantee
),
filtered AS (
    SELECT
        database_name,
        table_schema,
        table_name,
        grantee,
        privileges,
        CASE
            WHEN grantee = 'role_admin_bd' THEN 'ROLE_ADMIN_ATTENDU'
            WHEN grantee = 'role_exploitation' AND privileges IN ('SELECT') THEN 'ROLE_EXPLOITATION_ATTENDU'
            WHEN grantee = 'role_reporting' AND privileges IN ('SELECT') THEN 'ROLE_REPORTING_ATTENDU'
            WHEN grantee LIKE 'pg_%' THEN 'SYSTEME'
            ELSE 'A_ANALYSER'
        END AS grantee_category
    FROM privileges
)
SELECT
    database_name,
    table_schema,
    table_name,
    grantee,
    privileges,
    grantee_category,
    CASE
        WHEN grantee_category = 'A_ANALYSER' THEN 'PRIVILEGES_POTENTIELLEMENT_EXCESSIFS'
        ELSE 'OK'
    END AS status,
    CASE
        WHEN grantee_category = 'A_ANALYSER'
            THEN 'Revoir les privilèges accordés à ce rôle/utilisateur. Limiter au strict nécessaire.'
        ELSE 'Conformité aux profils attendus.'
    END AS recommendation
FROM filtered
WHERE grantee_category = 'A_ANALYSER'
ORDER BY table_schema, table_name, grantee;
