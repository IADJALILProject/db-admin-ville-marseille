-- security/audits_sql/check_weak_passwords.sql

SET search_path TO public;

SELECT
    current_database()                       AS database_name,
    r.rolname                                AS role_name,
    r.rolcanlogin                            AS can_login,
    r.rolsuper                               AS is_superuser,
    r.rolinherit                             AS is_inherit,
    r.rolvaliduntil                          AS password_valid_until,
    (r.rolpassword IS NULL)                  AS password_is_null,
    CASE
        WHEN r.rolsuper AND r.rolpassword IS NULL THEN 'CRITIQUE_SANS_MDP'
        WHEN r.rolcanlogin AND r.rolpassword IS NULL THEN 'A_RISQUE_SANS_MDP'
        WHEN r.rolsuper THEN 'SUPERUSER_AVEC_MDP'
        ELSE 'OK'
    END                                      AS status,
    CASE
        WHEN r.rolsuper AND r.rolpassword IS NULL
            THEN 'Définir immédiatement un mot de passe fort pour ce superutilisateur ou désactiver la connexion.'
        WHEN r.rolcanlogin AND r.rolpassword IS NULL
            THEN 'Définir un mot de passe fort ou transformer ce rôle en rôle sans connexion.'
        WHEN r.rolsuper
            THEN 'Vérifier la conformité du mot de passe et limiter l’usage de ce compte.'
        ELSE 'Vérifier la nécessité du compte et sa politique de mot de passe.'
    END                                      AS recommendation
FROM pg_authid r
WHERE r.rolcanlogin
ORDER BY status DESC, role_name;
-- security/audits_sql/check_weak_passwords.sql

SET search_path TO public;

SELECT
    current_database()                       AS database_name,
    r.rolname                                AS role_name,
    r.rolcanlogin                            AS can_login,
    r.rolsuper                               AS is_superuser,
    r.rolinherit                             AS is_inherit,
    r.rolvaliduntil                          AS password_valid_until,
    (r.rolpassword IS NULL)                  AS password_is_null,
    CASE
        WHEN r.rolsuper AND r.rolpassword IS NULL THEN 'CRITIQUE_SANS_MDP'
        WHEN r.rolcanlogin AND r.rolpassword IS NULL THEN 'A_RISQUE_SANS_MDP'
        WHEN r.rolsuper THEN 'SUPERUSER_AVEC_MDP'
        ELSE 'OK'
    END                                      AS status,
    CASE
        WHEN r.rolsuper AND r.rolpassword IS NULL
            THEN 'Définir immédiatement un mot de passe fort pour ce superutilisateur ou désactiver la connexion.'
        WHEN r.rolcanlogin AND r.rolpassword IS NULL
            THEN 'Définir un mot de passe fort ou transformer ce rôle en rôle sans connexion.'
        WHEN r.rolsuper
            THEN 'Vérifier la conformité du mot de passe et limiter l’usage de ce compte.'
        ELSE 'Vérifier la nécessité du compte et sa politique de mot de passe.'
    END                                      AS recommendation
FROM pg_authid r
WHERE r.rolcanlogin
ORDER BY status DESC, role_name;
