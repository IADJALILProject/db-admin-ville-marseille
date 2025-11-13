-- mysql/ddl/02_create_tables_mairie.sql

USE mairie_mysql;

CREATE TABLE IF NOT EXISTS citoyens (
    citoyen_id     INT          NOT NULL AUTO_INCREMENT,
    nom            VARCHAR(255) NOT NULL,
    prenom         VARCHAR(255) NOT NULL,
    date_naissance DATE         NOT NULL,
    email          VARCHAR(255) NOT NULL,
    telephone      VARCHAR(50)  NOT NULL,
    adresse        VARCHAR(500) NOT NULL,
    code_postal    CHAR(5)      NOT NULL,
    ville          VARCHAR(255) NOT NULL,
    arrondissement VARCHAR(4)   NOT NULL,
    date_creation  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (citoyen_id),
    KEY idx_citoyens_arrondissement (arrondissement),
    KEY idx_citoyens_code_postal (code_postal)
);

CREATE TABLE IF NOT EXISTS services_municipaux (
    service_id        INT          NOT NULL AUTO_INCREMENT,
    code_service      VARCHAR(64)  NOT NULL,
    nom_service       VARCHAR(255) NOT NULL,
    type_service      VARCHAR(255) NOT NULL,
    arrondissement    VARCHAR(4)   NOT NULL,
    email_contact     VARCHAR(255) NOT NULL,
    telephone_contact VARCHAR(50)  NOT NULL,
    est_actif         TINYINT(1)   NOT NULL DEFAULT 1,
    date_creation     DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (service_id),
    KEY idx_services_code (code_service),
    KEY idx_services_arrondissement (arrondissement)
);

CREATE TABLE IF NOT EXISTS demandes_rdv (
    rdv_id                  INT          NOT NULL AUTO_INCREMENT,
    citoyen_id              INT          NOT NULL,
    service_id              INT          NOT NULL,
    type_rdv                VARCHAR(64)  NOT NULL,
    date_demande            DATE         NOT NULL,
    date_rdv                DATE         NOT NULL,
    statut                  VARCHAR(32)  NOT NULL,
    canal                   VARCHAR(32)  NOT NULL,
    commentaire             VARCHAR(1000),
    rdv_start_ts            DATETIME,
    rdv_end_ts              DATETIME,
    slot_duration_min       INT,
    is_peak_hour            TINYINT(1),
    delai_jours_demande_rdv INT,
    date_insertion          DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (rdv_id),
    KEY idx_rdv_citoyen (citoyen_id),
    KEY idx_rdv_service_date (service_id, date_rdv),
    KEY idx_rdv_statut (statut)
);

CREATE TABLE IF NOT EXISTS demandes_etat_civil (
    demande_id      INT          NOT NULL AUTO_INCREMENT,
    citoyen_id      INT          NOT NULL,
    type_demande    VARCHAR(64)  NOT NULL,
    date_demande    DATE         NOT NULL,
    date_traitement DATE,
    statut          VARCHAR(32)  NOT NULL,
    mode_retrait    VARCHAR(32)  NOT NULL,
    date_insertion  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (demande_id),
    KEY idx_etat_civil_citoyen (citoyen_id),
    KEY idx_etat_civil_type (type_demande)
);

CREATE TABLE IF NOT EXISTS demandes_urbanisme (
    demande_id      INT          NOT NULL AUTO_INCREMENT,
    citoyen_id      INT          NOT NULL,
    type_demande    VARCHAR(64)  NOT NULL,
    adresse_projet  VARCHAR(500) NOT NULL,
    code_postal     CHAR(5)      NOT NULL,
    arrondissement  VARCHAR(4)   NOT NULL,
    date_demande    DATE         NOT NULL,
    date_decision   DATE,
    statut          VARCHAR(32)  NOT NULL,
    date_insertion  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (demande_id),
    KEY idx_urbanisme_citoyen (citoyen_id),
    KEY idx_urbanisme_arrondissement (arrondissement),
    KEY idx_urbanisme_type (type_demande)
);
