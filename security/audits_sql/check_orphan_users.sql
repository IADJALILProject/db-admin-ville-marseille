-- security/audits_sql/check_orphan_users.sql
-- Détection des rôles "orphelins" : comptes pouvant se connecter
-- mais sans objets possédés ni privilèges explicites sur des tables.

SET search_path TO public;

WITH login_roles AS (
    SELECT
        r.oid,
        r.rolname,
        r.rolcanlogin,
        r.rolsuper,
        r.rolcreatedb,
        r.rolcreaterole
    FROM pg_roles r
    WHERE r.rolcanlogin = TRUE
      AND r.rolname NOT LIKE 'pg_%'
      AND r.rolname NOT IN ('postgres')
),
owned_objects AS (
    SELECT DISTINCT
        relowner AS role_oid
    FROM pg_class
),
roles_with_table_priv AS (
    SELECT DISTINCT
        grantee AS rolname
    FROM information_schema.table_privileges
)
SELECT
    current_database()                                  AS database_name,
    lr.rolname                                          AS role_name,
    lr.rolcanlogin                                      AS can_login,
    lr.rolsuper                                         AS is_superuser,
    lr.rolcreatedb                                      AS can_createdb,
    lr.rolcreaterole                                    AS can_createrole,
    (oo.role_oid IS NULL)                               AS owns_no_objects,
    (tp.rolname IS NULL)                                AS has_no_table_privileges,
    CASE
        WHEN lr.rolcanlogin
         AND oo.role_oid IS NULL
         AND tp.rolname IS NULL
            THEN 'ORPHELIN_POTENTIEL'
        ELSE 'OK'
    END                                                 AS status,
    CASE
        WHEN lr.rolcanlogin
         AND oo.role_oid IS NULL
         AND tp.rolname IS NULL
            THEN 'Vérifier l''utilité de ce compte. Désactiver ou supprimer s''il est inutile.'
        ELSE 'Rôle utilisé ou disposant de privilèges. Vérifier périodiquement.'
    END                                                 AS recommendation
FROM login_roles lr
LEFT JOIN owned_objects      oo ON oo.role_oid = lr.oid
LEFT JOIN roles_with_table_priv tp ON tp.rolname = lr.rolname
ORDER BY status DESC, role_name;
