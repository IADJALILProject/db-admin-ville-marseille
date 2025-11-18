SET search_path TO metier, public;

SELECT setval(
  pg_get_serial_sequence('metier.demandes_rdv','rdv_id'),
  (SELECT COALESCE(MAX(rdv_id), 0) + 1 FROM metier.demandes_rdv),
  false
);

SELECT setval(
  pg_get_serial_sequence('metier.citoyens','citoyen_id'),
  (SELECT COALESCE(MAX(citoyen_id), 0) + 1 FROM metier.citoyens),
  false
);
