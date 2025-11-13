-- mysql/maintenance/20_analyze_tables.sql

USE mairie_mysql;

ANALYZE TABLE
    citoyens,
    services_municipaux,
    demandes_rdv,
    demandes_etat_civil,
    demandes_urbanisme;
