-- mysql/dml/10_load_from_csv.sql

USE mairie_mysql;

LOAD DATA INFILE '/app/data/sources/citoyens.csv'
INTO TABLE citoyens
CHARACTER SET utf8mb4
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(citoyen_id, nom, prenom, date_naissance, email, telephone, adresse, code_postal, ville, arrondissement);

LOAD DATA INFILE '/app/data/sources/services_municipaux.csv'
INTO TABLE services_municipaux
CHARACTER SET utf8mb4
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(service_id, code_service, nom_service, type_service, arrondissement, email_contact, telephone_contact);

LOAD DATA INFILE '/app/data/sources/demandes_rdv.csv'
INTO TABLE demandes_rdv
CHARACTER SET utf8mb4
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(rdv_id, citoyen_id, service_id, type_rdv, date_demande, date_rdv, statut, canal, commentaire);

LOAD DATA INFILE '/app/data/sources/demandes_etat_civil.csv'
INTO TABLE demandes_etat_civil
CHARACTER SET utf8mb4
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(demande_id, citoyen_id, type_demande, date_demande, date_traitement, statut, mode_retrait);

LOAD DATA INFILE '/app/data/sources/demandes_urbanisme.csv'
INTO TABLE demandes_urbanisme
CHARACTER SET utf8mb4
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(demande_id, citoyen_id, type_demande, adresse_projet, code_postal, arrondissement, date_demande, date_decision, statut);
