db-admin-ville-marseille/
├─ README.md
├─ .gitignore
├─ docker-compose.yml              # pour lancer Postgres/MySQL/MSSQL localement
│
├─ docs/
│  ├─ 00_contexte_marseille.md     # résumé DSI, poste i8530-M, objectifs de la démo
│  ├─ 01_architecture_si_bdd.md    # schéma logique SI mairie (services, usagers, applis)
│  ├─ 02_bonnes_pratiques_admin_bd.md
│  ├─ 03_politique_sauvegarde_pra_pca.md
│  ├─ 04_procedures_exploitation_journaliere.md
│  ├─ 05_procedures_incident_critique.md
│  ├─ 06_securite_et_droits_acces.md
│  └─ 07_guide_entretien_poste_i8530M.md  # ce que tu raconteras à l’oral
│
├─ config/
│  ├─ config_global.yml            # chemins backup, rétention, mail alert, etc.
│  ├─ config_postgres.yml
│  ├─ config_mysql.yml
│  ├─ config_mssql.yml
│  └─ logging.yml                  # config logging Python
│
├─ data/
│  ├─ sources/                     # “données brutes” comme si elles venaient d’applis
│  │  ├─ citoyens.csv
│  │  ├─ services_municipaux.csv
│  │  ├─ demandes_rdv.csv
│  │  ├─ demandes_etat_civil.csv
│  │  └─ demandes_urbanisme.csv
│  ├─ generated/                   # données générées par scripts Python (simulation)
│  │  ├─ citoyens_enrichis.csv
│  │  ├─ rdv_planifies.csv
│  │  └─ stats_quotidiennes.csv
│  └─ README_data.md               # explique le contexte “Ville de Marseille”
│
├─ db/
│  ├─ postgres/
│  │  ├─ ddl/
│  │  │  ├─ 01_create_schema_referentiel.sql
│  │  │  ├─ 02_create_schema_metier.sql
│  │  │  ├─ 03_create_tables_referentiel.sql     # services, arrondissements, etc.
│  │  │  ├─ 04_create_tables_citoyens_rdv.sql    # citoyens, rdv, demandes
│  │  │  ├─ 05_indexes_constraints.sql
│  │  │  └─ 06_views_reporting.sql               # vues pour les applis mairie
│  │  ├─ dml/
│  │  │  ├─ 10_seed_referentiel.sql              # services, types de demandes
│  │  │  └─ 11_insert_demo_from_csv.sql         # chargements depuis /data
│  │  ├─ maintenance/
│  │  │  ├─ 20_analyze_vacuum.sql
│  │  │  ├─ 21_index_usage_report.sql
│  │  │  └─ 22_long_running_queries.sql
│  │  └─ security/
│  │     ├─ 30_create_roles_and_users.sql        # rôle “agent_mairie”, “lecture_reporting”, etc.
│  │     ├─ 31_grant_privileges_by_app.sql
│  │     └─ 32_row_level_security_citoyens.sql   # ex : filtrage par arrondissement
│  │
│  ├─ mysql/
│  │  ├─ ddl/         # même logique mais plus simple
│  │  ├─ dml/
│  │  └─ maintenance/
│  │
│  └─ mssql/
│     ├─ ddl/
│     ├─ dml/
│     └─ maintenance/
│
├─ scripts/
│  └─ python/
│     ├─ __init__.py
│     ├─ db_utils.py                # connexions, retries, logs
│     ├─ simulate_data.py           # génère /data/generated pour le contexte mairie
│     ├─ manage_schemas.py          # applique ddl/dml pour créer/mettre à jour les DB
│     ├─ backup_runner.py           # orchestre pg_dump / mysqldump / BACKUP DATABASE
│     ├─ restore_runner.py          # scénarios de restauration PRA
│     ├─ health_checks.py           # ping DB, sessions, taille, latence
│     ├─ perf_metrics_collector.py  # collecte stats (taille tables, temps requêtes)
│     ├─ security_audit.py          # exécute scripts d’audit SQL et produit un rapport
│     ├─ scheduler.py               # planification simple (APScheduler / schedule)
│     └─ generate_reports.py        # rapports markdown/HTML pour les équipes DSI
│
├─ templates/
│  ├─ report_perf_template.md
│  ├─ report_security_template.md
│  └─ email_alert_template.md
│
├─ ansible/
│  ├─ inventory/
│  │  └─ hosts.ini                  # liste des serveurs de BDD (simulation : 1 VM)
│  ├─ group_vars/
│  │  └─ db_servers.yml             # variables : version postgres, chemins scripts…
│  ├─ playbooks/
│  │  ├─ install_postgres.yml       # installe PostgreSQL + paquets requis
│  │  ├─ deploy_db_admin_scripts.yml# pousse tes scripts Python sur le serveur
│  │  └─ hardening_db_servers.yml   # durcissement de base (droits, services inutiles)
│  └─ roles/
│     ├─ common/
│     │  ├─ tasks/main.yml          # paquets communs, répertoires backup/scripts
│     │  └─ files/
│     └─ postgres/
│        ├─ tasks/main.yml          # installation et config PostgreSQL
│        ├─ templates/postgresql.conf.j2
│        ├─ templates/pg_hba.conf.j2
│        └─ handlers/main.yml
│
├─ monitoring/
│  ├─ exporters/
│  │  └─ metrics_http_server.py     # petit serveur HTTP exposant métriques JSON
│  ├─ samples_grafana/
│  │  ├─ dashboard_postgres_marseille.json
│  │  └─ dashboard_global_bdd.json
│  └─ kpi_definition.md             # disponibilité, temps de réponse, volumétrie, etc.
│
├─ security/
│  ├─ audits_sql/
│  │  ├─ check_public_schema.sql
│  │  ├─ check_weak_passwords.sql
│  │  ├─ check_orphan_users.sql
│  │  └─ check_excessive_privileges.sql
│  └─ security_policy.md            # politique d’accès pour la mairie (agents, appli, etc.)
│
├─ backups/
│  ├─ postgres/
│  │  ├─ README_backups_postgres.md # explique la stratégie (full + incrémental simulé)
│  │  └─ (répertoire où tes scripts vont déposer les dumps)
│  ├─ mysql/
│  └─ mssql/
│
└─ tests/
   ├─ test_db_utils.py
   ├─ test_backup_runner.py
   ├─ test_health_checks.py
   └─ scenarios_pra/
      ├─ 01_perte_instance_postgres.md
      ├─ 02_restoration_from_last_full.md
      └─ 03_corruption_table_demande_rdv.md
