# 🏛️ DB-Admin – Ville de Marseille
Projet complet de gestion, supervision et sécurisation d’environnements de bases de données dans un cadre DataOps.

---

## 1. Contexte
Ce projet met en œuvre une plateforme d’administration et de supervision multi-SGBD inspirée du fonctionnement de la Ville de Marseille.  
Il démontre la maîtrise du cycle complet d’un environnement DataOps : déploiement, supervision, sauvegarde, restauration, sécurité et automatisation.

Objectifs :
- Déploiement reproductible et automatisé
- Observabilité et collecte de métriques
- Sauvegarde et PRA
- Audits SQL et sécurité
- Transactions et logique métier
- Automatisation via Ansible

---

## 2. Stack technique

| Domaine | Technologies |
|----------|--------------|
| Conteneurisation | Docker Compose |
| Automatisation | Ansible |
| Bases de données | PostgreSQL 15, MySQL 8, MSSQL 2022 |
| Langage | Python 3.12 |
| Bibliothèques Python | psycopg2, logging, subprocess, json |
| Monitoring | Grafana, fichiers CSV/JSON |
| CI/CD Data | manage_schemas.py, backup_runner.py, restore_runner.py |

---

## 3. Arborescence et bonnes pratiques

```
db-admin-ville-marseille/
├─ docker-compose.yml
├─ requirements.txt
├─ .venv/
│
├─ ansible/
│  ├─ inventory/hosts.ini
│  ├─ group_vars/db_servers.yml
│  ├─ playbooks/
│  │  ├─ install_postgres.yml
│  │  ├─ deploy_db_admin_scripts.yml
│  │  └─ hardening_db_servers.yml
│  └─ roles/
│     ├─ common/
│     │  └─ tasks/main.yml
│     └─ postgres/
│        ├─ tasks/main.yml
│        ├─ templates/postgresql.conf.j2
│        ├─ templates/pg_hba.conf.j2
│        └─ handlers/main.yml
│
├─ db/
│  └─ postgres/
│     ├─ ddl/
│     │  ├─ 01_create_schema_referentiel.sql
│     │  ├─ 02_create_schema_metier.sql
│     │  ├─ 03_create_tables_referentiel.sql
│     │  ├─ 04_create_tables_citoyens_rdv.sql
│     │  ├─ 05_indexes_constraints.sql
│     │  ├─ 06_views_reporting.sql
│     │  └─ 07_functions_rdv.sql
│     ├─ dml/
│     │  ├─ 10_seed_referentiel.sql
│     │  ├─ 11_insert_demo_from_csv.sql
│     │  └─ 12_reseed_sequences.sql
│     └─ maintenance/
│        ├─ 20_analyze_vacuum.sql
│        ├─ 21_index_usage_report.sql
│        └─ 22_long_running_queries.sql
│
├─ scripts/
│  └─ python/
│     ├─ db_utils.py
│     ├─ manage_schemas.py
│     ├─ backup_runner.py
│     ├─ restore_runner.py
│     ├─ health_checks.py
│     ├─ perf_metrics_collector.py
│     ├─ security_audit.py
│     └─ python_rdv_transactions_demo.py
│
├─ monitoring/
│  ├─ status/
│  ├─ snapshots/
│  └─ grafana_dashboard.json
│
├─ security/
│  ├─ sql/
│  │  ├─ check_public_schema.sql
│  │  ├─ check_weak_passwords.sql
│  │  ├─ check_orphan_users.sql
│  │  └─ check_excessive_privileges.sql
│  └─ audit_results/
│
├─ backups/
├─ data/
├─ tests/
└─ README.md
```

**Bonnes pratiques adoptées :**
- Découpage clair DDL / DML / maintenance / sécurité
- Convention de nommage stricte (ordre numérique des scripts SQL)
- Centralisation du logging dans `db_utils.py`
- Isolation des environnements Python (.venv)
- Versioning des sauvegardes par horodatage
- Modularité totale compatible CI/CD

---

## 4. Déploiement

```bash
docker compose up -d
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/python/manage_schemas.py
```

---

## 5. Modules Python

| Script | Fonction |
|---------|-----------|
| `manage_schemas.py` | Exécute les scripts SQL dans l’ordre et crée la base complète |
| `health_checks.py` | Vérifie la santé de PostgreSQL et produit un JSON de statut |
| `perf_metrics_collector.py` | Mesure la volumétrie et la taille des tables |
| `backup_runner.py` | Effectue des sauvegardes PostgreSQL automatisées |
| `restore_runner.py` | Restaure les dumps et recrée la base |
| `security_audit.py` | Lance les contrôles SQL et génère des rapports CSV |
| `python_rdv_transactions_demo.py` | Simule des transactions PL/pgSQL avec rollback et commit |

---

## 6. Sécurité et audits

Les scripts dans `security/sql/` exécutent des vérifications automatisées :
- Permissions publiques non autorisées
- Utilisateurs orphelins
- Privilèges excessifs
- Mots de passe faibles

Les résultats sont sauvegardés dans `security/audit_results/` et exportables vers Grafana.

---

## 7. Monitoring

Les métriques sont collectées sous forme de fichiers CSV et JSON :  
- Latence, connexions, verrous, taille des tables  
- Résultats d’audits et volumétrie globale

Les dashboards Grafana utilisent la datasource "File" pour afficher :
- Disponibilité SGBD
- Taille des schémas et indexes
- Tendances de volumétrie et santé

---

## 8. Transactions et logique métier

Fonctions principales (`07_functions_rdv.sql`) :
- `creer_demande_rdv()` : crée un rendez-vous avec validations et contraintes
- `annuler_demande_rdv()` : annule un RDV avec justification et traçabilité

Le script `python_rdv_transactions_demo.py` démontre les transactions (commit et rollback).

---

## 9. Automatisation Ansible

Ansible pilote l’installation, la sauvegarde et les audits :
- `install_postgres.yml` : installe et configure PostgreSQL
- `deploy_db_admin_scripts.yml` : déploie les scripts Python et SQL
- `hardening_db_servers.yml` : durcissement de la sécurité et nettoyage des droits

Intégrable dans un pipeline CI/CD ou planifié via Cron.

---

## 10. Roadmap

- Intégration Prometheus / OpenTelemetry
- Exposition API REST (FastAPI)
- Déploiement cloud (Azure / AWS RDS)
- Extension des audits sécurité
- Centralisation Grafana + AlertManager

---

## Auteur
**Djalil Salah-Bey**  
Data Engineer – DataOps & Platform Engineering  
📧 salahbeydjalil@gmail.com
