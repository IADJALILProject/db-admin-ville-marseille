-- 30_create_roles_and_users.sql

SET search_path TO public;

DO
$$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'role_admin_bd') THEN
        CREATE ROLE role_admin_bd NOINHERIT LOGIN;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'role_exploitation') THEN
        CREATE ROLE role_exploitation NOINHERIT;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'role_reporting') THEN
        CREATE ROLE role_reporting NOINHERIT;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'role_service_etat_civil') THEN
        CREATE ROLE role_service_etat_civil NOINHERIT;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'role_service_urbanisme') THEN
        CREATE ROLE role_service_urbanisme NOINHERIT;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'role_service_accueil') THEN
        CREATE ROLE role_service_accueil NOINHERIT;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'role_app_portail_citoyen') THEN
        CREATE ROLE role_app_portail_citoyen NOINHERIT;
    END IF;
END
$$;

-- Exemple d’utilisateurs techniques (à adapter dans un vrai contexte)
DO
$$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'dba_marseille') THEN
        CREATE ROLE dba_marseille LOGIN PASSWORD 'CHANGE_ME';
        GRANT role_admin_bd TO dba_marseille;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'exploit_marseille') THEN
        CREATE ROLE exploit_marseille LOGIN PASSWORD 'CHANGE_ME';
        GRANT role_exploitation TO exploit_marseille;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'reporting_marseille') THEN
        CREATE ROLE reporting_marseille LOGIN PASSWORD 'CHANGE_ME';
        GRANT role_reporting TO reporting_marseille;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'app_portail_citoyen') THEN
        CREATE ROLE app_portail_citoyen LOGIN PASSWORD 'CHANGE_ME';
        GRANT role_app_portail_citoyen TO app_portail_citoyen;
    END IF;
END
$$;
