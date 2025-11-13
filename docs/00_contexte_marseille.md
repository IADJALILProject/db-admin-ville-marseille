# Contexte du projet – Ville de Marseille

## Objectif

Ce projet a pour objectif de démontrer, sur un environnement réduit, la façon dont un administrateur de bases de données peut :

- Concevoir, configurer et administrer des SGBD pour une collectivité comme la Ville de Marseille.
- Mettre en place des sauvegardes, des procédures de restauration et un début de PRA/PCA.
- Assurer la sécurité, la qualité et la performance des bases de données.
- Automatiser les tâches d’exploitation à l’aide de scripts Python et d’Ansible.
- Documenter les procédures pour les équipes d’exploitation de la DSI.

Le projet est aligné sur les besoins d’une DSI de collectivité, et plus particulièrement sur le poste d’administrateur de bases de données au sein de la Ville de Marseille.

## Périmètre fonctionnel simulé

Le système d’information simulé couvre des besoins typiques d’une mairie :

- Gestion des citoyens (données de base, coordonnées, arrondissement).
- Gestion des services municipaux (état civil, urbanisme, rendez-vous, petite enfance, etc.).
- Gestion des demandes et rendez-vous (prise de rendez-vous, statut, historique).
- Production de données de reporting pour les directions métier.

Ces données sont stockées principalement dans PostgreSQL, avec des exemples de scripts prévus pour MySQL et SQL Server afin d’illustrer la polyvalence sur plusieurs SGBD.

## Périmètre technique

Le projet couvre :

- Administration logique des bases (schémas, tables, index, droits).
- Sauvegarde et restauration des bases (PostgreSQL en priorité).
- Automatisation des tâches d’exploitation récurrentes.
- Collecte de métriques de performance et d’état de santé.
- Mise en place d’audits de sécurité sur les privilèges et rôles.
- Déploiement automatisé d’une partie de l’infrastructure via Ansible.

Le tout est pensé pour être exploitable sur un environnement de développement local (Docker) tout en restant transposable à un contexte serveur on-premise.

## Public cible

Cette documentation s’adresse :

- Aux administrateurs de bases de données.
- Aux ingénieurs systèmes et DevOps impliqués dans l’infrastructure.
- Aux chefs de projets applicatifs souhaitant comprendre les contraintes BD.
- Aux responsables de la DSI en charge de la qualité de service et de la sécurité.

Elle doit permettre de comprendre rapidement comment le socle BD est conçu, exploité et supervisé, et comment il pourrait être étendu à un contexte de production réel.
