-- mssql/dml/10_bulk_load_from_csv.sql

USE MairieMSSQL;
GO

TRUNCATE TABLE referentiel.services_municipaux;
TRUNCATE TABLE metier.demandes_rdv;
TRUNCATE TABLE metier.demandes_etat_civil;
TRUNCATE TABLE metier.demandes_urbanisme;
TRUNCATE TABLE metier.citoyens;
GO

BULK INSERT referentiel.services_municipaux
FROM 'C:\data\sources\services_municipaux.csv'
WITH (
    FIRSTROW = 2,
    FIELDTERMINATOR = ',',
    ROWTERMINATOR = '0x0A',
    TABLOCK,
    CODEPAGE = '65001'
);

BULK INSERT metier.citoyens
FROM 'C:\data\sources\citoyens.csv'
WITH (
    FIRSTROW = 2,
    FIELDTERMINATOR = ',',
    ROWTERMINATOR = '0x0A',
    TABLOCK,
    CODEPAGE = '65001'
);

BULK INSERT metier.demandes_rdv
FROM 'C:\data\sources\demandes_rdv.csv'
WITH (
    FIRSTROW = 2,
    FIELDTERMINATOR = ',',
    ROWTERMINATOR = '0x0A',
    TABLOCK,
    CODEPAGE = '65001'
);

BULK INSERT metier.demandes_etat_civil
FROM 'C:\data\sources\demandes_etat_civil.csv'
WITH (
    FIRSTROW = 2,
    FIELDTERMINATOR = ',',
    ROWTERMINATOR = '0x0A',
    TABLOCK,
    CODEPAGE = '65001'
);

BULK INSERT metier.demandes_urbanisme
FROM 'C:\data\sources\demandes_urbanisme.csv'
WITH (
    FIRSTROW = 2,
    FIELDTERMINATOR = ',',
    ROWTERMINATOR = '0x0A',
    TABLOCK,
    CODEPAGE = '65001'
);
GO
