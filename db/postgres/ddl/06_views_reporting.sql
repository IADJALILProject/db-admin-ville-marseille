SET search_path TO reporting, metier, referentiel, public;

CREATE OR REPLACE VIEW reporting.v_rdv_par_jour_service AS
SELECT
    r.date_rdv,
    s.code_service,
    s.nom_service,
    s.arrondissement       AS arrondissement_service,
    COUNT(*)               AS nb_rdv_total,
    COUNT(*) FILTER (WHERE r.statut = 'CONFIRME') AS nb_rdv_confirme,
    COUNT(*) FILTER (WHERE r.statut = 'HONORE')   AS nb_rdv_honore,
    COUNT(*) FILTER (WHERE r.statut = 'ANNULE')   AS nb_rdv_annule
FROM metier.demandes_rdv r
JOIN referentiel.services_municipaux s
  ON r.service_id = s.service_id
GROUP BY r.date_rdv, s.code_service, s.nom_service, s.arrondissement;

CREATE OR REPLACE VIEW reporting.v_charge_quotidienne AS
SELECT
    sq.date,
    sq.nb_rdv_total,
    sq.nb_rdv_confirme,
    sq.nb_rdv_honore,
    sq.nb_rdv_annule,
    sq.nb_dem_etat_civil,
    sq.nb_dem_urbanisme,
    sq.nb_citoyens_distincts
FROM (
    SELECT
        d.date_demande AS date,
        COUNT(DISTINCT d.rdv_id)                                 AS nb_rdv_total,
        COUNT(*) FILTER (WHERE d.statut = 'CONFIRME')            AS nb_rdv_confirme,
        COUNT(*) FILTER (WHERE d.statut = 'HONORE')              AS nb_rdv_honore,
        COUNT(*) FILTER (WHERE d.statut = 'ANNULE')              AS nb_rdv_annule,
        0                                                        AS nb_dem_etat_civil,
        0                                                        AS nb_dem_urbanisme,
        COUNT(DISTINCT d.citoyen_id)                             AS nb_citoyens_distincts
    FROM metier.demandes_rdv d
    GROUP BY d.date_demande

    UNION ALL

    SELECT
        e.date_demande AS date,
        0                                                 AS nb_rdv_total,
        0                                                 AS nb_rdv_confirme,
        0                                                 AS nb_rdv_honore,
        0                                                 AS nb_rdv_annule,
        COUNT(DISTINCT e.demande_id)                      AS nb_dem_etat_civil,
        0                                                 AS nb_dem_urbanisme,
        COUNT(DISTINCT e.citoyen_id)                      AS nb_citoyens_distincts
    FROM metier.demandes_etat_civil e
    GROUP BY e.date_demande

    UNION ALL

    SELECT
        u.date_demande AS date,
        0                                                 AS nb_rdv_total,
        0                                                 AS nb_rdv_confirme,
        0                                                 AS nb_rdv_honore,
        0                                                 AS nb_rdv_annule,
        0                                                 AS nb_dem_etat_civil,
        COUNT(DISTINCT u.demande_id)                      AS nb_dem_urbanisme,
        COUNT(DISTINCT u.citoyen_id)                      AS nb_citoyens_distincts
    FROM metier.demandes_urbanisme u
    GROUP BY u.date_demande
) sq
GROUP BY sq.date,
         sq.nb_rdv_total,
         sq.nb_rdv_confirme,
         sq.nb_rdv_honore,
         sq.nb_rdv_annule,
         sq.nb_dem_etat_civil,
         sq.nb_dem_urbanisme,
         sq.nb_citoyens_distincts;

CREATE OR REPLACE VIEW reporting.v_citoyens_activite AS
SELECT
    c.citoyen_id,
    c.nom,
    c.prenom,
    c.arrondissement,
    COUNT(DISTINCT r.rdv_id)           AS nb_rdv,
    COUNT(DISTINCT ec.demande_id)      AS nb_demandes_etat_civil,
    COUNT(DISTINCT u.demande_id)       AS nb_demandes_urbanisme,
    MAX(r.date_rdv)                    AS last_rdv_date,
    MIN(dates.date_demande)            AS first_demande_date,
    MAX(dates.date_demande)            AS last_demande_date
FROM metier.citoyens c
LEFT JOIN metier.demandes_rdv r
       ON r.citoyen_id = c.citoyen_id
LEFT JOIN metier.demandes_etat_civil ec
       ON ec.citoyen_id = c.citoyen_id
LEFT JOIN metier.demandes_urbanisme u
       ON u.citoyen_id = c.citoyen_id
LEFT JOIN (
    SELECT citoyen_id, date_demande
    FROM metier.demandes_rdv
    UNION ALL
    SELECT citoyen_id, date_demande
    FROM metier.demandes_etat_civil
    UNION ALL
    SELECT citoyen_id, date_demande
    FROM metier.demandes_urbanisme
) dates
       ON dates.citoyen_id = c.citoyen_id
GROUP BY c.citoyen_id, c.nom, c.prenom, c.arrondissement;
