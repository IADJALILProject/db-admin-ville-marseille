-- db/postgres/ddl/05_indexes_constraints.sql
SET search_path TO metier, referentiel, public;

---------------------------
-- Normalize & dedupe emails BEFORE uniqueness
---------------------------

-- Normalize: trim + lower (skip NULLs)
UPDATE metier.citoyens
SET email = lower(trim(email))
WHERE email IS NOT NULL
  AND (email <> lower(trim(email)));

-- Remove exact duplicates on normalized email, keep the smallest citoyen_id
WITH d AS (
  SELECT citoyen_id,
         row_number() OVER (PARTITION BY email ORDER BY citoyen_id) AS rn
  FROM metier.citoyens
  WHERE email IS NOT NULL
)
DELETE FROM metier.citoyens c
USING d
WHERE c.citoyen_id = d.citoyen_id
  AND d.rn > 1;

---------------------------
-- Foreign keys (idempotent)
---------------------------

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint
     WHERE conname = 'fk_citoyens_arrondissement'
       AND conrelid = 'metier.citoyens'::regclass
  ) THEN
    ALTER TABLE metier.citoyens
      ADD CONSTRAINT fk_citoyens_arrondissement
      FOREIGN KEY (arrondissement)
      REFERENCES referentiel.arrondissements(code_arrondissement);
  END IF;
END$$;

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint
     WHERE conname = 'fk_rdv_citoyen'
       AND conrelid = 'metier.demandes_rdv'::regclass
  ) THEN
    ALTER TABLE metier.demandes_rdv
      ADD CONSTRAINT fk_rdv_citoyen
      FOREIGN KEY (citoyen_id)
      REFERENCES metier.citoyens(citoyen_id);
  END IF;
END$$;

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint
     WHERE conname = 'fk_rdv_service'
       AND conrelid = 'metier.demandes_rdv'::regclass
  ) THEN
    ALTER TABLE metier.demandes_rdv
      ADD CONSTRAINT fk_rdv_service
      FOREIGN KEY (service_id)
      REFERENCES referentiel.services_municipaux(service_id);
  END IF;
END$$;

-- type_rdv référence le code (SOCIAL, URBANISME, ...)
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint
     WHERE conname = 'fk_rdv_type'
       AND conrelid = 'metier.demandes_rdv'::regclass
  ) THEN
    ALTER TABLE metier.demandes_rdv
      ADD CONSTRAINT fk_rdv_type
      FOREIGN KEY (type_rdv)
      REFERENCES referentiel.types_rdv(code_type_rdv);
  END IF;
END$$;

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint
     WHERE conname = 'fk_etatcivil_citoyen'
       AND conrelid = 'metier.demandes_etat_civil'::regclass
  ) THEN
    ALTER TABLE metier.demandes_etat_civil
      ADD CONSTRAINT fk_etatcivil_citoyen
      FOREIGN KEY (citoyen_id)
      REFERENCES metier.citoyens(citoyen_id);
  END IF;
END$$;

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint
     WHERE conname = 'fk_etatcivil_type'
       AND conrelid = 'metier.demandes_etat_civil'::regclass
  ) THEN
    ALTER TABLE metier.demandes_etat_civil
      ADD CONSTRAINT fk_etatcivil_type
      FOREIGN KEY (type_demande)
      REFERENCES referentiel.types_demande_etat_civil(code_type_etat_civil);
  END IF;
END$$;

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint
     WHERE conname = 'fk_urbanisme_citoyen'
       AND conrelid = 'metier.demandes_urbanisme'::regclass
  ) THEN
    ALTER TABLE metier.demandes_urbanisme
      ADD CONSTRAINT fk_urbanisme_citoyen
      FOREIGN KEY (citoyen_id)
      REFERENCES metier.citoyens(citoyen_id);
  END IF;
END$$;

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint
     WHERE conname = 'fk_urbanisme_type'
       AND conrelid = 'metier.demandes_urbanisme'::regclass
  ) THEN
    ALTER TABLE metier.demandes_urbanisme
      ADD CONSTRAINT fk_urbanisme_type
      FOREIGN KEY (type_demande)
      REFERENCES referentiel.types_demande_urbanisme(code_type_urbanisme);
  END IF;
END$$;

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint
     WHERE conname = 'fk_urbanisme_arrondissement'
       AND conrelid = 'metier.demandes_urbanisme'::regclass
  ) THEN
    ALTER TABLE metier.demandes_urbanisme
      ADD CONSTRAINT fk_urbanisme_arrondissement
      FOREIGN KEY (arrondissement)
      REFERENCES referentiel.arrondissements(code_arrondissement);
  END IF;
END$$;

---------------------------
-- Indexes (idempotent)
---------------------------

-- Unicité email après normalisation + dédoublonnage
CREATE UNIQUE INDEX IF NOT EXISTS idx_citoyens_email
  ON metier.citoyens(email);

CREATE INDEX IF NOT EXISTS idx_rdv_citoyen  ON metier.demandes_rdv(citoyen_id);
CREATE INDEX IF NOT EXISTS idx_rdv_service  ON metier.demandes_rdv(service_id);
CREATE INDEX IF NOT EXISTS idx_rdv_type     ON metier.demandes_rdv(type_rdv);
CREATE INDEX IF NOT EXISTS idx_rdv_date     ON metier.demandes_rdv(date_rdv);
CREATE INDEX IF NOT EXISTS idx_rdv_statut   ON metier.demandes_rdv(statut);
CREATE INDEX IF NOT EXISTS idx_rdv_canal    ON metier.demandes_rdv(canal);

CREATE INDEX IF NOT EXISTS idx_urb_arrondissement
  ON metier.demandes_urbanisme(arrondissement);

CREATE INDEX IF NOT EXISTS idx_urb_dates
  ON metier.demandes_urbanisme(date_demande, date_decision);
