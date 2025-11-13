# Architecture du SI simulé – Volet Bases de Données

## Vue d’ensemble

L’architecture simulée représente un sous-ensemble du système d’information d’une mairie :

- Un SGBD principal PostgreSQL hébergeant les données critiques (citoyens, services, demandes, rendez-vous).
- Des SGBD secondaires (MySQL, SQL Server) utilisés pour illustrer la capacité à administrer plusieurs moteurs.
- Des scripts Python d’administration et de monitoring exécutés depuis un serveur d’exploitation.
- Un outillage de supervision exploitant les métriques exposées par les scripts.

La topologie reste volontairement simple mais respecte une séparation claire entre les rôles :

- Serveurs de bases de données.
- Serveur d’exploitation / scripts.
- Outils de supervision.

## Schéma logique des données

Le schéma PostgreSQL est structuré en plusieurs espaces :

- Schéma `referentiel` :
  - Tables des services municipaux.
  - Tables des arrondissements.
  - Tables des types de demandes.
- Schéma `metier` :
  - Table des citoyens.
  - Table des demandes (état civil, urbanisme, etc.).
  - Table des rendez-vous.
  - Tables de journalisation éventuellement nécessaires.
- Vues de reporting :
  - Vues d’agrégation par service, par type de demande, par arrondissement.
  - Vues destinées à l’exposition vers des outils décisionnels ou des applications.

Cette structuration permet de séparer les référentiels, les données métiers et les couches de consommation.

## Composants techniques

### SGBD

- PostgreSQL comme SGBD principal.
- MySQL et SQL Server utilisés comme exemples complémentaires.

Pour chaque SGBD, le projet contient :

- Des scripts DDL (création de schémas, tables, index).
- Des scripts DML de chargement de données de démonstration.
- Des scripts de maintenance (analyse, nettoyage, rapports d’index).

### Scripts d’administration

Les scripts Python assurent :

- La création et la mise à jour des schémas.
- Les sauvegardes et restaurations.
- Les checks de santé (connectivité, espace, sessions).
- La collecte de métriques techniques.
- L’exécution d’audits de sécurité.

Ils sont conçus pour être configurables via des fichiers YAML et orchestrés par un scheduler simple ou par des outils d’ordonnancement externes.

### Supervision

Le projet expose des métriques via un petit serveur HTTP Python. Des exemples de dashboards Grafana sont fournis pour illustrer :

- Le suivi des temps de réponse de certaines requêtes.
- La volumétrie des bases et des tables clés.
- Le statut des dernières sauvegardes.

## Flux principaux

1. Chargement des données simulées (fichiers CSV) dans PostgreSQL.
2. Exécution des scripts d’administration pour la création des schémas et le chargement.
3. Planification de sauvegardes régulières via `backup_runner.py`.
4. Exécution périodique de `health_checks.py` et `perf_metrics_collector.py`.
5. Exécution régulière d’audits de sécurité via `security_audit.py`.
6. Visualisation synthétique dans les dashboards de supervision.

Cette architecture peut être étendue à plusieurs serveurs ou intégrée à une infrastructure existante de la collectivité.
