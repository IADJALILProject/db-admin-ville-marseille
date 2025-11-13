# Stratégie de sauvegarde PostgreSQL – Base « mairie »

Ce répertoire contient les sauvegardes générées pour la base de données PostgreSQL principale utilisée dans le contexte « Ville de Marseille ». Il est alimenté par les scripts d’administration du dépôt (`scripts/python/backup_runner.py`).

## 1. Objectifs

- Disposer d’une sauvegarde régulière et exploitable de la base `mairie`.
- Limiter la perte de données à une durée compatible avec les besoins métiers.
- Pouvoir tester et documenter les scénarios de restauration dans le cadre du PRA.

Cette stratégie est volontairement simplifiée pour la démonstration, mais suit les principes d’une exploitation réelle.

## 2. Types de sauvegardes

Dans cette maquette, les sauvegardes sont réalisées à l’aide de `pg_dump` au format personnalisé (`-F c`).

- **Sauvegarde complète logique (full)**
  - Contient l’ensemble des objets (schémas, tables, données, rôles liés à la base).
  - Format compressé, adapté à la restauration ciblée.
  - Fichier généré dans ce répertoire avec un nom du type :

    ```text
    mairie_full_YYYYMMDD_HHMMSS.dump
    ```

- **Incrémentiel simulé**
  - La mise en place d’un véritable incrémentiel (WAL archiving, PITR) n’est pas implémentée dans cette démonstration.
  - Le concept d’« incrémentiel » est évoqué dans la documentation PRA, mais non activé techniquement.
  - Pour un contexte réel, il conviendrait de compléter la solution avec :
    - L’archivage des journaux de transactions (WAL).
    - Un schéma de restauration point-in-time (PITR).

## 3. Fonctionnement du script `backup_runner.py`

Le script lit les paramètres de sauvegarde dans :

- `config/config_global.yml` (section `backup.postgres`)
- `config/config_postgres.yml` (section `connection`)

Principales étapes :

1. Vérification que les sauvegardes sont **activées** (`enabled: true`).
2. Construction du chemin de destination (répertoire `backups/postgres` par défaut).
3. Génération du nom de fichier basé sur :
   - Le nom de la base (`mairie`).
   - La date et l’heure d’exécution.
4. Lancement de `pg_dump` avec les paramètres adéquats (hôte, port, utilisateur, base, format).
5. Écriture du fichier `.dump` dans ce répertoire.
6. Rotation des fichiers anciens en fonction du nombre de jours de rétention configuré.

## 4. Rétention et rotation

La rétention est définie dans `config/config_global.yml`, section :

```yaml
backup:
  postgres:
    dir: "./backups/postgres"
    retention_days: 14
