-- db/postgres/dml/10_seed_referentiel.sql
SET search_path TO referentiel, public;

-- ======================
-- Arrondissements
-- ======================
INSERT INTO referentiel.arrondissements (code_arrondissement, nom_arrondissement, code_postal_prefix)
VALUES
    ('1e',  '1er arrondissement',  '13001'),
    ('2e',  '2e arrondissement',   '13002'),
    ('3e',  '3e arrondissement',   '13003'),
    ('4e',  '4e arrondissement',   '13004'),
    ('5e',  '5e arrondissement',   '13005'),
    ('6e',  '6e arrondissement',   '13006'),
    ('7e',  '7e arrondissement',   '13007'),
    ('8e',  '8e arrondissement',   '13008'),
    ('9e',  '9e arrondissement',   '13009'),
    ('10e', '10e arrondissement',  '13010'),
    ('11e', '11e arrondissement',  '13011'),
    ('12e', '12e arrondissement',  '13012'),
    ('13e', '13e arrondissement',  '13013'),
    ('14e', '14e arrondissement',  '13014'),
    ('15e', '15e arrondissement',  '13015'),
    ('16e', '16e arrondissement',  '13016')
ON CONFLICT (code_arrondissement) DO UPDATE
SET nom_arrondissement = EXCLUDED.nom_arrondissement,
    code_postal_prefix = EXCLUDED.code_postal_prefix;

-- ======================
-- Services municipaux
-- - GÉNÈRE un code_service NON NULL (SVC-01, SVC-02, ...)
-- - Donne des valeurs par défaut cohérentes pour les autres colonnes
-- ======================
INSERT INTO referentiel.services_municipaux
    (service_id, code_service, nom_service, type_service, arrondissement, email_contact, telephone_contact)
SELECT
    x AS service_id,
    'SVC-' || lpad(x::text, 2, '0')        AS code_service,
    'Service ' || x                        AS nom_service,
    'Guichet'                              AS type_service,
    (( ( (x - 1) % 16) + 1 )::text) || 'e' AS arrondissement,
    'service' || x || '@marseille.fr'      AS email_contact,
    '04 91 00 ' || lpad((1000 + x)::text, 4, '0') AS telephone_contact
FROM generate_series(1, 16) AS x
ON CONFLICT (service_id) DO UPDATE
SET code_service      = EXCLUDED.code_service,
    nom_service       = EXCLUDED.nom_service,
    type_service      = EXCLUDED.type_service,
    arrondissement    = EXCLUDED.arrondissement,
    email_contact     = EXCLUDED.email_contact,
    telephone_contact = EXCLUDED.telephone_contact;

-- ======================
-- Types état civil
-- ======================
INSERT INTO referentiel.types_demande_etat_civil (code_type_etat_civil, libelle)
VALUES
    ('ACTE_NAISSANCE', 'Acte de naissance'),
    ('ACTE_MARIAGE',   'Acte de mariage'),
    ('ACTE_DECES',     'Acte de décès'),
    ('LIVRET_FAMILLE', 'Livret de famille')
ON CONFLICT (code_type_etat_civil) DO UPDATE
SET libelle = EXCLUDED.libelle;

-- ======================
-- Types urbanisme
-- ======================
INSERT INTO referentiel.types_demande_urbanisme (code_type_urbanisme, libelle)
VALUES
    ('PERMIS_CONSTRUIRE',     'Permis de construire'),
    ('DECLARATION_PREALABLE', 'Déclaration préalable'),
    ('AUTORISATION_TRAVAUX',  'Autorisation de travaux')
ON CONFLICT (code_type_urbanisme) DO UPDATE
SET libelle = EXCLUDED.libelle;

-- ======================
-- Types RDV (inclut SOCIAL)
-- ======================
INSERT INTO referentiel.types_rdv (code_type_rdv, libelle)
VALUES
    ('ETAT_CIVIL',  'Rendez-vous état civil'),
    ('URBANISME',   'Rendez-vous urbanisme'),
    ('CITOYENNETE', 'Citoyenneté'),
    ('SOCIAL',      'Rendez-vous social'),
    ('SPORT',       'Sports'),
    ('SCOLARITE',   'Scolarité')
ON CONFLICT (code_type_rdv) DO UPDATE
SET libelle = EXCLUDED.libelle;

-- ======================
-- Canaux de contact
-- ======================
INSERT INTO referentiel.canaux_contact (code_canal, libelle)
VALUES
    ('EN_LIGNE',  'En ligne'),
    ('TELEPHONE', 'Téléphone'),
    ('GUICHET',   'Guichet')
ON CONFLICT (code_canal) DO UPDATE
SET libelle = EXCLUDED.libelle;
