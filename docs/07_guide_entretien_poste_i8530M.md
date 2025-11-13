# Guide de préparation à l’entretien – Poste Administrateur BD

## Objectif

Structurer la présentation du projet démonstratif pour illustrer les compétences attendues sur le poste d’administrateur de bases de données.

## Introduction (profil et rôle)

Points à présenter en ouverture :

- Rôle visé : administrateur de bases de données au sein d’une DSI de collectivité.
- Expérience sur les SGBD (PostgreSQL en priorité, exposition à d’autres moteurs).
- Intérêt pour l’automatisation, la fiabilité du run et la sécurité des données.

## Présentation du projet

Expliquer brièvement :

- Le contexte simulé : une mairie gérant des citoyens, des services et des demandes.
- Le périmètre du projet :
  - Administration logique des bases.
  - Sauvegarde, restauration, PRA/PCA.
  - Sécurité et audits.
  - Performance et supervision.
  - Automatisation et documentation.

Mettre en avant que le projet est conçu comme un socle de démonstration, transposable à un environnement réel.

## Points techniques à valoriser

### 1. Administration multi-SGBD

- Scripts de création de schémas et tables pour PostgreSQL (et exemples pour MySQL/SQL Server).
- Gestion structurée des objets (schémas référentiel, métier, reporting).

### 2. Sauvegardes et restauration

- Script `backup_runner.py` pour les sauvegardes régulières.
- Script `restore_runner.py` et scénarios de tests de restauration documentés.
- Politique de rétention et principes de PRA/PCA.

### 3. Sécurité et droits d’accès

- Modèle de rôles et utilisateurs pour séparer les profils (administration, exploitation, métiers).
- Scripts d’audit de sécurité et rapport associé.
- Réflexion sur les données sensibles et la protection des sauvegardes.

### 4. Performance et supervision

- Scripts de maintenance et de collecte de métriques.
- Exemples de dashboards de supervision (volumétrie, temps de réponse, disponibilité).
- Notion d’indicateurs et de seuils d’alerte.

### 5. Automatisation et Ansible

- Automatisation des tâches d’administration via Python.
- Exemple d’usage d’Ansible pour :
  - Installer et configurer PostgreSQL.
  - Déployer les scripts d’administration.
  - Appliquer un début de hardening serveur.

Mettre en avant la capacité à travailler dans une logique d’infra-as-code.

## Positionnement et soft skills

Insister sur :

- La rigueur dans la gestion des sauvegardes et des changements.
- L’esprit de service vis-à-vis des équipes métiers (disponibilité, continuité).
- La capacité à documenter et à transmettre (docs, procédures, rapports).
- L’envie de travailler en équipe avec les systèmes, réseaux, projets et sécurité.

## Questions à préparer

Quelques exemples de questions possibles et axes de réponse :

- Comment prioriser les restaurations en cas d’incident majeur ?
- Comment aborder la sécurisation des accès pour une nouvelle application métier ?
- Comment traiter une demande de performance sur une base très sollicitée ?
- Comment organiser la documentation pour qu’elle soit utile à l’exploitation ?

Le projet servira de support pour illustrer les réponses, avec des exemples concrets tirés des scripts, des configurations et des documents fournis dans le dépôt.
