-- 32_row_level_security_citoyens.sql

SET search_path TO metier, public;

ALTER TABLE metier.citoyens ENABLE ROW LEVEL SECURITY;

CREATE OR REPLACE FUNCTION metier.current_citoyen_id() RETURNS integer
LANGUAGE plpgsql
STABLE
AS
$$
DECLARE
    v_setting text;
BEGIN
    BEGIN
        v_setting := current_setting('app.citoyen_id', true);
    EXCEPTION
        WHEN others THEN
            v_setting := NULL;
    END;

    IF v_setting IS NULL OR v_setting = '' THEN
        RETURN NULL;
    END IF;

    RETURN v_setting::integer;
END;
$$;

DROP POLICY IF EXISTS citoyens_self_access ON metier.citoyens;

CREATE POLICY citoyens_self_access
ON metier.citoyens
FOR SELECT
TO role_app_portail_citoyen
USING (
    citoyen_id = metier.current_citoyen_id()
);

ALTER TABLE metier.demandes_rdv ENABLE ROW LEVEL SECURITY;
ALTER TABLE metier.demandes_etat_civil ENABLE ROW LEVEL SECURITY;
ALTER TABLE metier.demandes_urbanisme ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS rdv_self_access ON metier.demandes_rdv;
DROP POLICY IF EXISTS etat_civil_self_access ON metier.demandes_etat_civil;
DROP POLICY IF EXISTS urbanisme_self_access ON metier.demandes_urbanisme;

CREATE POLICY rdv_self_access
ON metier.demandes_rdv
FOR SELECT
TO role_app_portail_citoyen
USING (
    citoyen_id = metier.current_citoyen_id()
);

CREATE POLICY etat_civil_self_access
ON metier.demandes_etat_civil
FOR SELECT
TO role_app_portail_citoyen
USING (
    citoyen_id = metier.current_citoyen_id()
);

CREATE POLICY urbanisme_self_access
ON metier.demandes_urbanisme
FOR SELECT
TO role_app_portail_citoyen
USING (
    citoyen_id = metier.current_citoyen_id()
);
