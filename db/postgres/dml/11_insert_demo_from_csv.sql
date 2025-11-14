SET search_path TO metier, referentiel, public;
TRUNCATE TABLE
  metier.demandes_urbanisme,
  metier.demandes_etat_civil,
  metier.demandes_rdv,
  metier.citoyens
RESTART IDENTITY CASCADE;

DROP TABLE IF EXISTS _stg_services_municipaux;
CREATE TEMP TABLE _stg_services_municipaux
(
    service_id        BIGINT,
    code_service      TEXT,
    nom_service       TEXT,
    type_service      TEXT,
    arrondissement    TEXT,
    email_contact     TEXT,
    telephone_contact TEXT
);

COPY _stg_services_municipaux
FROM '/app/data/sources/services_municipaux.csv'
WITH (FORMAT csv, HEADER true, DELIMITER ',', ENCODING 'UTF8');

INSERT INTO referentiel.services_municipaux
    (service_id, code_service, nom_service, type_service, arrondissement, email_contact, telephone_contact)
SELECT
    s.service_id,
    NULLIF(TRIM(s.code_service), ''),
    NULLIF(TRIM(s.nom_service), ''),
    NULLIF(TRIM(s.type_service), ''),
    NULLIF(TRIM(s.arrondissement), ''),
    NULLIF(TRIM(s.email_contact), ''),
    NULLIF(TRIM(s.telephone_contact), '')
FROM _stg_services_municipaux s
ON CONFLICT (service_id) DO UPDATE
SET code_service      = COALESCE(EXCLUDED.code_service,      referentiel.services_municipaux.code_service),
    nom_service       = COALESCE(EXCLUDED.nom_service,       referentiel.services_municipaux.nom_service),
    type_service      = COALESCE(EXCLUDED.type_service,      referentiel.services_municipaux.type_service),
    arrondissement    = COALESCE(EXCLUDED.arrondissement,    referentiel.services_municipaux.arrondissement),
    email_contact     = COALESCE(EXCLUDED.email_contact,     referentiel.services_municipaux.email_contact),
    telephone_contact = COALESCE(EXCLUDED.telephone_contact, referentiel.services_municipaux.telephone_contact);


DROP TABLE IF EXISTS _stg_citoyens;
CREATE TEMP TABLE _stg_citoyens
(
    citoyen_id     BIGINT,
    nom            TEXT,
    prenom         TEXT,
    date_naissance DATE,
    email          TEXT,
    telephone      TEXT,
    adresse        TEXT,
    code_postal    TEXT,
    ville          TEXT,
    arrondissement TEXT
);

COPY _stg_citoyens
FROM '/app/data/sources/citoyens.csv'
WITH (FORMAT csv, HEADER true, DELIMITER ',', ENCODING 'UTF8');

INSERT INTO metier.citoyens
    (citoyen_id, nom, prenom, date_naissance, email, telephone, adresse, code_postal, ville, arrondissement)
SELECT
    c.citoyen_id,
    NULLIF(TRIM(c.nom), ''),
    NULLIF(TRIM(c.prenom), ''),
    c.date_naissance,
    lower(NULLIF(TRIM(c.email), '')),
    NULLIF(TRIM(c.telephone), ''),
    NULLIF(TRIM(c.adresse), ''),
    NULLIF(TRIM(c.code_postal), ''),
    NULLIF(TRIM(c.ville), ''),
    NULLIF(TRIM(c.arrondissement), '')
FROM _stg_citoyens c
ON CONFLICT (citoyen_id) DO UPDATE
SET nom            = EXCLUDED.nom,
    prenom         = EXCLUDED.prenom,
    date_naissance = EXCLUDED.date_naissance,
    email          = EXCLUDED.email,
    telephone      = EXCLUDED.telephone,
    adresse        = EXCLUDED.adresse,
    code_postal    = EXCLUDED.code_postal,
    ville          = EXCLUDED.ville,
    arrondissement = EXCLUDED.arrondissement;

DROP TABLE IF EXISTS _stg_demandes_rdv;
CREATE TEMP TABLE _stg_demandes_rdv
(
    rdv_id        BIGINT,
    citoyen_id    BIGINT,
    service_id    BIGINT,
    type_rdv_txt  TEXT,   
    date_rdv      DATE,
    statut        TEXT,
    canal_txt     TEXT,  
);

COPY _stg_demandes_rdv (rdv_id,citoyen_id,service_id,type_rdv_txt,date_demande,date_rdv,statut,canal_txt,commentaire)
FROM '/app/data/sources/demandes_rdv.csv'
WITH (FORMAT csv, HEADER true, DELIMITER ',', ENCODING 'UTF8');

WITH m AS (
  SELECT
      s.rdv_id,
      s.citoyen_id,
      s.service_id,
      COALESCE(t_code.code_type_rdv, t_lib.code_type_rdv) AS type_rdv_code,
      s.date_demande,
      s.date_rdv,
      UPPER(TRIM(s.statut)) AS statut_norm,
      COALESCE(c_code.code_canal, c_lib.code_canal)       AS canal_code,
      s.commentaire
  FROM _stg_demandes_rdv s
  LEFT JOIN referentiel.types_rdv t_code
         ON t_code.code_type_rdv = UPPER(TRIM(s.type_rdv_txt))
  LEFT JOIN referentiel.types_rdv t_lib
         ON t_lib.libelle ILIKE TRIM(s.type_rdv_txt)
  LEFT JOIN referentiel.canaux_contact c_code
         ON c_code.code_canal = UPPER(TRIM(s.canal_txt))
  LEFT JOIN referentiel.canaux_contact c_lib
         ON c_lib.libelle ILIKE TRIM(s.canal_txt)
)
INSERT INTO metier.demandes_rdv
    (rdv_id, citoyen_id, service_id, type_rdv, date_demande, date_rdv, statut, canal, commentaire)
SELECT
    rdv_id, citoyen_id, service_id, type_rdv_code, date_demande, date_rdv,
    statut_norm, canal_code, commentaire
FROM m
WHERE type_rdv_code IS NOT NULL
  AND canal_code    IS NOT NULL;

DROP TABLE IF EXISTS _stg_dem_ec;
CREATE TEMP TABLE _stg_dem_ec
(
    demande_id       BIGINT,
    citoyen_id       BIGINT,
    type_demande_txt TEXT,
    date_demande     DATE,
    date_traitement  DATE,
    statut           TEXT,
    mode_retrait     TEXT
);

COPY _stg_dem_ec
FROM '/app/data/sources/demandes_etat_civil.csv'
WITH (FORMAT csv, HEADER true, DELIMITER ',', ENCODING 'UTF8');

WITH m AS (
  SELECT
      s.demande_id,
      s.citoyen_id,
      COALESCE(ec_code.code_type_etat_civil, ec_lib.code_type_etat_civil) AS type_demande_code,
      s.date_demande,
      s.date_traitement,
      UPPER(TRIM(s.statut)) AS statut_norm,
      s.mode_retrait
  FROM _stg_dem_ec s
  LEFT JOIN referentiel.types_demande_etat_civil ec_code
         ON ec_code.code_type_etat_civil = UPPER(TRIM(s.type_demande_txt))
  LEFT JOIN referentiel.types_demande_etat_civil ec_lib
         ON ec_lib.libelle ILIKE TRIM(s.type_demande_txt)
)
INSERT INTO metier.demandes_etat_civil
    (demande_id, citoyen_id, type_demande, date_demande, date_traitement, statut, mode_retrait)
SELECT
    demande_id, citoyen_id, type_demande_code, date_demande, date_traitement, statut_norm, mode_retrait
FROM m
WHERE type_demande_code IS NOT NULL;


DROP TABLE IF EXISTS _stg_dem_urb;
CREATE TEMP TABLE _stg_dem_urb
(
    demande_id       BIGINT,
    citoyen_id       BIGINT,
    type_demande_txt TEXT,
    adresse_projet   TEXT,
    code_postal      TEXT,
    arrondissement   TEXT,
    date_demande     DATE,
    date_decision    DATE,
    statut           TEXT
);

COPY _stg_dem_urb
FROM '/app/data/sources/demandes_urbanisme.csv'
WITH (FORMAT csv, HEADER true, DELIMITER ',', ENCODING 'UTF8');

WITH m AS (
  SELECT
      s.demande_id,
      s.citoyen_id,
      COALESCE(u_code.code_type_urbanisme, u_lib.code_type_urbanisme) AS type_demande_code,
      s.adresse_projet,
      s.code_postal,
      s.arrondissement,
      s.date_demande,
      s.date_decision,
      UPPER(TRIM(s.statut)) AS statut_norm
  FROM _stg_dem_urb s
  LEFT JOIN referentiel.types_demande_urbanisme u_code
         ON u_code.code_type_urbanisme = UPPER(TRIM(s.type_demande_txt))
  LEFT JOIN referentiel.types_demande_urbanisme u_lib
         ON u_lib.libelle ILIKE TRIM(s.type_demande_txt)
)
INSERT INTO metier.demandes_urbanisme
    (demande_id, citoyen_id, type_demande, adresse_projet, code_postal, arrondissement,
     date_demande, date_decision, statut)
SELECT
    demande_id, citoyen_id, type_demande_code, adresse_projet, code_postal, arrondissement,
    date_demande, date_decision, statut_norm
FROM m
WHERE type_demande_code IS NOT NULL;
