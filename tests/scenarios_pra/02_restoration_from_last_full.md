

```md
# 02 – Scénario PRA : Restauration depuis la dernière sauvegarde complète

## Objectif

Décrire et tester la restauration de la base `mairie` à partir de la dernière sauvegarde complète disponible, en se plaçant dans le cas d’une base corrompue ou d’une erreur opérationnelle majeure.

## Pré-requis

- Accès au répertoire de sauvegarde : `backups/postgres/`.
- Présence d’au moins un fichier de sauvegarde `*.dump` valide.
- Scripts Python d’administration disponibles et exécutables :
  - `backup_runner.py`
  - `restore_runner.py`
- Droits suffisants pour :
  - Accéder à l’instance PostgreSQL.
  - Créer / supprimer la base de données `mairie`.

## Étapes détaillées

### 1. Identification de la sauvegarde à utiliser

1. Lister le contenu du répertoire des sauvegardes :

   ```bash
   ls -1 backups/postgres
