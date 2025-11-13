-- mssql/ddl/02_create_tables_mairie.sql

USE MairieMSSQL;
GO

IF NOT EXISTS (SELECT 1 FROM sys.schemas WHERE name = N'referentiel')
    EXEC('CREATE SCHEMA referentiel');
GO

IF NOT EXISTS (SELECT 1 FROM sys.schemas WHERE name = N'metier')
    EXEC('CREATE SCHEMA metier');
GO

IF OBJECT_ID('metier.citoyens', 'U') IS NULL
BEGIN
    CREATE TABLE metier.citoyens (
        citoyen_id     INT            IDENTITY(1,1) NOT NULL PRIMARY KEY,
        nom            NVARCHAR(255)  NOT NULL,
        prenom         NVARCHAR(255)  NOT NULL,
        date_naissance DATE           NOT NULL,
        email          NVARCHAR(255)  NOT NULL,
        telephone      NVARCHAR(50)   NOT NULL,
        adresse        NVARCHAR(500)  NOT NULL,
        code_postal    CHAR(5)        NOT NULL,
        ville          NVARCHAR(255)  NOT NULL,
        arrondissement NVARCHAR(4)    NOT NULL,
        date_creation  DATETIME2(0)   NOT NULL DEFAULT SYSDATETIME()
    );

    CREATE INDEX IX_citoyens_arrondissement ON metier.citoyens (arrondissement);
    CREATE INDEX IX_citoyens_code_postal    ON metier.citoyens (code_postal);
END;
GO

IF OBJECT_ID('referentiel.services_municipaux', 'U') IS NULL
BEGIN
    CREATE TABLE referentiel.services_municipaux (
        service_id        INT            IDENTITY(1,1) NOT NULL PRIMARY KEY,
        code_service      NVARCHAR(64)   NOT NULL,
        nom_service       NVARCHAR(255)  NOT NULL,
        type_service      NVARCHAR(255)  NOT NULL,
        arrondissement    NVARCHAR(4)    NOT NULL,
        email_contact     NVARCHAR(255)  NOT NULL,
        telephone_contact NVARCHAR(50)   NOT NULL,
        est_actif         BIT            NOT NULL DEFAULT 1,
        date_creation     DATETIME2(0)   NOT NULL DEFAULT SYSDATETIME()
    );

    CREATE INDEX IX_services_code          ON referentiel.services_municipaux (code_service);
    CREATE INDEX IX_services_arrondissement ON referentiel.services_municipaux (arrondissement);
END;
GO

IF OBJECT_ID('metier.demandes_rdv', 'U') IS NULL
BEGIN
    CREATE TABLE metier.demandes_rdv (
        rdv_id                  INT            IDENTITY(1,1) NOT NULL PRIMARY KEY,
        citoyen_id              INT            NOT NULL,
        service_id              INT            NOT NULL,
        type_rdv                NVARCHAR(64)   NOT NULL,
        date_demande            DATE           NOT NULL,
        date_rdv                DATE           NOT NULL,
        statut                  NVARCHAR(32)   NOT NULL,
        canal                   NVARCHAR(32)   NOT NULL,
        commentaire             NVARCHAR(1000) NULL,
        rdv_start_ts            DATETIME2(0)   NULL,
        rdv_end_ts              DATETIME2(0)   NULL,
        slot_duration_min       INT            NULL,
        is_peak_hour            BIT            NULL,
        delai_jours_demande_rdv INT            NULL,
        date_insertion          DATETIME2(0)   NOT NULL DEFAULT SYSDATETIME()
    );

    CREATE INDEX IX_rdv_citoyen          ON metier.demandes_rdv (citoyen_id);
    CREATE INDEX IX_rdv_service_date     ON metier.demandes_rdv (service_id, date_rdv);
    CREATE INDEX IX_rdv_statut           ON metier.demandes_rdv (statut);
END;
GO

IF OBJECT_ID('metier.demandes_etat_civil', 'U') IS NULL
BEGIN
    CREATE TABLE metier.demandes_etat_civil (
        demande_id      INT            IDENTITY(1,1) NOT NULL PRIMARY KEY,
        citoyen_id      INT            NOT NULL,
        type_demande    NVARCHAR(64)   NOT NULL,
        date_demande    DATE           NOT NULL,
        date_traitement DATE           NULL,
        statut          NVARCHAR(32)   NOT NULL,
        mode_retrait    NVARCHAR(32)   NOT NULL,
        date_insertion  DATETIME2(0)   NOT NULL DEFAULT SYSDATETIME()
    );

    CREATE INDEX IX_etat_civil_citoyen ON metier.demandes_etat_civil (citoyen_id);
    CREATE INDEX IX_etat_civil_type    ON metier.demandes_etat_civil (type_demande);
END;
GO

IF OBJECT_ID('metier.demandes_urbanisme', 'U') IS NULL
BEGIN
    CREATE TABLE metier.demandes_urbanisme (
        demande_id      INT            IDENTITY(1,1) NOT NULL PRIMARY KEY,
        citoyen_id      INT            NOT NULL,
        type_demande    NVARCHAR(64)   NOT NULL,
        adresse_projet  NVARCHAR(500)  NOT NULL,
        code_postal     CHAR(5)        NOT NULL,
        arrondissement  NVARCHAR(4)    NOT NULL,
        date_demande    DATE           NOT NULL,
        date_decision   DATE           NULL,
        statut          NVARCHAR(32)   NOT NULL,
        date_insertion  DATETIME2(0)   NOT NULL DEFAULT SYSDATETIME()
    );

    CREATE INDEX IX_urbanisme_citoyen       ON metier.demandes_urbanisme (citoyen_id);
    CREATE INDEX IX_urbanisme_arrondissement ON metier.demandes_urbanisme (arrondissement);
    CREATE INDEX IX_urbanisme_type          ON metier.demandes_urbanisme (type_demande);
END;
GO
