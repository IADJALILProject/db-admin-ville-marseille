-- 20_analyze_vacuum.sql

SET search_path TO metier, referentiel, public;

VACUUM (ANALYZE) metier.citoyens;
VACUUM (ANALYZE) metier.demandes_rdv;
VACUUM (ANALYZE) metier.demandes_etat_civil;
VACUUM (ANALYZE) metier.demandes_urbanisme;

VACUUM (ANALYZE) referentiel.arrondissements;
VACUUM (ANALYZE) referentiel.services_municipaux;
VACUUM (ANALYZE) referentiel.types_demande_etat_civil;
VACUUM (ANALYZE) referentiel.types_demande_urbanisme;
VACUUM (ANALYZE) referentiel.types_rdv;
VACUUM (ANALYZE) referentiel.canaux_contact;
