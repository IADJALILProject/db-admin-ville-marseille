# 01 – Scénario PRA : Perte d’instance PostgreSQL

## Objectif

Simuler la perte totale de l’instance PostgreSQL hébergeant la base `mairie` et vérifier la capacité à :

- Restaurer la base à partir de la dernière sauvegarde disponible.
- Remettre en service les principaux objets métiers.
- Documenter les actions réalisées et les points d’attention.

## Contexte

- Base principale : `mairie`
- SGBD : PostgreSQL
- Emplacement des sauvegardes : `backups/postgres/`
- Outils utilisés :
  - Script `backup_runner.py` pour la création des sauvegardes.
  - Script `restore_runner.py` pour la restauration.
  - Documentation associée aux procédures PRA.

## Hypothèse d’incident

L’instance PostgreSQL est considérée comme indisponible suite à :

- Une panne matérielle du serveur hébergeant la base.
- Ou une corruption majeure de l’instance nécessitant une réinstallation.

Dans le cadre de cette maquette, l’incident est simulé par :

- L’arrêt de l’instance existante.
- La suppression de la base `mairie` avant restauration sur une instance saine.

## Étapes de gestion de la perte d’instance

### 1. Détection et qualification

1. Les outils de supervision signalent :
   - L’indisponibilité de l’instance (échec des checks de connectivité).
   - L’impossibilité de joindre la base `mairie`.
2. L’équipe d’exploitation confirme :
   - L’impossibilité d’établir une connexion SQL.
   - L’impact sur les applications métiers concernées.

### 2. Stabilisation

1. Arrêter les tentatives de connexion répétées provenant de batchs ou scripts si nécessaire.
2. Informer les interlocuteurs métiers de l’interruption de service.
3. Confirmer la décision de restaurer la base à partir de la dernière sauvegarde.

### 3. Préparation de l’environnement cible

1. Disposer d’une instance PostgreSQL fonctionnelle (réinstallée ou de secours).
2. Vérifier :
   - Le niveau de version PostgreSQL compatible avec les sauvegardes.
   - L’espace disque disponible pour la base et les sauvegardes.
3. Copier les fichiers de sauvegarde pertinents dans `backups/postgres/` si nécessaire.

### 4. Restauration de la base `mairie`

1. Identifier la sauvegarde à utiliser :
   - De préférence, la sauvegarde complète la plus récente générée par `backup_runner.py`.
2. Lancer la restauration en ligne de commande, par exemple :

   ```bash
   cd scripts/python
   python restore_runner.py --backup-dir ../../backups/postgres
