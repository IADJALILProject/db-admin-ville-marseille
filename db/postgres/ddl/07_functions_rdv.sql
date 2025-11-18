SET search_path TO metier, referentiel, public;

CREATE TABLE IF NOT EXISTS metier.histo_demandes_rdv (
    histo_id        BIGSERIAL PRIMARY KEY,
    rdv_id          BIGINT      NOT NULL,
    ancien_statut   TEXT        NOT NULL,
    nouveau_statut  TEXT        NOT NULL,
    commentaire     TEXT,
    changed_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    changed_by      TEXT        NOT NULL,
    CONSTRAINT fk_histo_rdv
        FOREIGN KEY (rdv_id) REFERENCES metier.demandes_rdv(rdv_id)
);

CREATE OR REPLACE FUNCTION metier.creer_demande_rdv(
    p_citoyen_id    BIGINT,
    p_service_id    BIGINT,
    p_type_rdv      TEXT,
    p_date_demande  DATE,
    p_date_rdv      DATE,
    p_canal         TEXT,
    p_commentaire   TEXT DEFAULT NULL
)
RETURNS BIGINT
LANGUAGE plpgsql
AS $$
DECLARE
    v_rdv_id       BIGINT;
    v_code_rdv     TEXT;
    v_code_canal   TEXT;
    v_exists_cit   BOOLEAN;
    v_exists_srv   BOOLEAN;
BEGIN
    SELECT t.code_type_rdv
      INTO v_code_rdv
      FROM referentiel.types_rdv t
     WHERE t.code_type_rdv = UPPER(TRIM(p_type_rdv))
        OR t.libelle ILIKE TRIM(p_type_rdv)
     LIMIT 1;

    IF v_code_rdv IS NULL THEN
        RAISE EXCEPTION 'Type de RDV "%" inconnu', p_type_rdv
            USING ERRCODE = 'foreign_key_violation';
    END IF;

    SELECT c.code_canal
      INTO v_code_canal
      FROM referentiel.canaux_contact c
     WHERE c.code_canal = UPPER(TRIM(p_canal))
        OR c.libelle ILIKE TRIM(p_canal)
     LIMIT 1;

    IF v_code_canal IS NULL THEN
        RAISE EXCEPTION 'Canal "%" inconnu', p_canal
            USING ERRCODE = 'foreign_key_violation';
    END IF;

    SELECT EXISTS(SELECT 1 FROM metier.citoyens WHERE citoyen_id = p_citoyen_id)
      INTO v_exists_cit;
    IF NOT v_exists_cit THEN
        RAISE EXCEPTION 'Citoyen % inexistant', p_citoyen_id
            USING ERRCODE = 'foreign_key_violation';
    END IF;

    SELECT EXISTS(SELECT 1 FROM referentiel.services_municipaux WHERE service_id = p_service_id)
      INTO v_exists_srv;
    IF NOT v_exists_srv THEN
        RAISE EXCEPTION 'Service % inexistant', p_service_id
            USING ERRCODE = 'foreign_key_violation';
    END IF;

    IF p_date_rdv < p_date_demande THEN
        RAISE EXCEPTION 'La date de RDV (%) ne peut pas être antérieure à la date de demande (%)',
            p_date_rdv, p_date_demande
            USING ERRCODE = 'invalid_datetime_format';
    END IF;

    INSERT INTO metier.demandes_rdv (
        citoyen_id, service_id, type_rdv, date_demande, date_rdv, statut, canal, commentaire
    )
    VALUES (
        p_citoyen_id, p_service_id, v_code_rdv, p_date_demande, p_date_rdv,
        'EN_ATTENTE', v_code_canal, p_commentaire
    )
    RETURNING rdv_id INTO v_rdv_id;

    RETURN v_rdv_id;
END;
$$;

CREATE OR REPLACE PROCEDURE metier.annuler_demande_rdv(
    p_rdv_id      BIGINT,
    p_commentaire TEXT,
    p_changed_by  TEXT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_ancien_statut  TEXT;
BEGIN
    SELECT statut
      INTO v_ancien_statut
      FROM metier.demandes_rdv
     WHERE rdv_id = p_rdv_id
     FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Demande de RDV % introuvable', p_rdv_id
            USING ERRCODE = 'no_data_found';
    END IF;

    IF v_ancien_statut = 'ANNULE' THEN
        INSERT INTO metier.histo_demandes_rdv (rdv_id, ancien_statut, nouveau_statut, commentaire, changed_by)
        VALUES (p_rdv_id, v_ancien_statut, v_ancien_statut, COALESCE(p_commentaire,'Annulation redondante'), p_changed_by);
        RETURN;
    END IF;

    UPDATE metier.demandes_rdv
       SET statut = 'ANNULE',
           commentaire = CASE
               WHEN p_commentaire IS NULL THEN commentaire
               WHEN commentaire IS NULL THEN p_commentaire
               ELSE commentaire || ' | ' || p_commentaire
           END
     WHERE rdv_id = p_rdv_id;

    INSERT INTO metier.histo_demandes_rdv (rdv_id, ancien_statut, nouveau_statut, commentaire, changed_by)
    VALUES (p_rdv_id, v_ancien_statut, 'ANNULE', p_commentaire, p_changed_by);
END;
$$;
