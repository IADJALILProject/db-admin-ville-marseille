-- 31_grant_privileges_by_app.sql

SET search_path TO public;

REVOKE ALL ON SCHEMA referentiel, metier, reporting FROM PUBLIC;
REVOKE ALL ON ALL TABLES IN SCHEMA referentiel FROM PUBLIC;
REVOKE ALL ON ALL TABLES IN SCHEMA metier FROM PUBLIC;
REVOKE ALL ON ALL TABLES IN SCHEMA reporting FROM PUBLIC;

GRANT USAGE ON SCHEMA referentiel, metier, reporting TO role_admin_bd;
GRANT ALL ON SCHEMA referentiel, metier, reporting TO role_admin_bd;
GRANT ALL ON ALL TABLES IN SCHEMA referentiel TO role_admin_bd;
GRANT ALL ON ALL TABLES IN SCHEMA metier TO role_admin_bd;
GRANT ALL ON ALL TABLES IN SCHEMA reporting TO role_admin_bd;
GRANT ALL ON ALL SEQUENCES IN SCHEMA metier TO role_admin_bd;

GRANT USAGE ON SCHEMA referentiel, metier, reporting TO role_exploitation;
GRANT SELECT ON ALL TABLES IN SCHEMA referentiel TO role_exploitation;
GRANT SELECT ON ALL TABLES IN SCHEMA metier TO role_exploitation;
GRANT SELECT ON ALL TABLES IN SCHEMA reporting TO role_exploitation;

GRANT USAGE ON SCHEMA reporting TO role_reporting;
GRANT SELECT ON ALL TABLES IN SCHEMA reporting TO role_reporting;

GRANT USAGE ON SCHEMA referentiel, metier TO role_service_etat_civil;
GRANT SELECT ON referentiel.arrondissements,
             referentiel.services_municipaux,
             referentiel.types_demande_etat_civil
    TO role_service_etat_civil;
GRANT SELECT, INSERT, UPDATE ON metier.demandes_etat_civil TO role_service_etat_civil;
GRANT SELECT ON metier.citoyens TO role_service_etat_civil;

GRANT USAGE ON SCHEMA referentiel, metier TO role_service_urbanisme;
GRANT SELECT ON referentiel.arrondissements,
             referentiel.services_municipaux,
             referentiel.types_demande_urbanisme
    TO role_service_urbanisme;
GRANT SELECT, INSERT, UPDATE ON metier.demandes_urbanisme TO role_service_urbanisme;
GRANT SELECT ON metier.citoyens TO role_service_urbanisme;

GRANT USAGE ON SCHEMA referentiel, metier TO role_service_accueil;
GRANT SELECT ON referentiel.arrondissements,
             referentiel.services_municipaux,
             referentiel.canaux_contact,
             referentiel.types_rdv
    TO role_service_accueil;
GRANT SELECT, INSERT, UPDATE ON metier.demandes_rdv TO role_service_accueil;
GRANT SELECT ON metier.citoyens TO role_service_accueil;

GRANT USAGE ON SCHEMA metier, reporting TO role_app_portail_citoyen;
GRANT SELECT ON reporting.v_citoyens_activite,
             reporting.v_rdv_par_jour_service,
             reporting.v_charge_quotidienne
    TO role_app_portail_citoyen;
GRANT SELECT ON metier.citoyens,
             metier.demandes_rdv,
             metier.demandes_etat_civil,
             metier.demandes_urbanisme
    TO role_app_portail_citoyen;
