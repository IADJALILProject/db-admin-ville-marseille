

```md
# 03 – Scénario PRA : Corruption de la table `demandes_rdv`

## Objectif

Simuler une corruption logique de la table `metier.demandes_rdv` et décrire les options de restauration possibles, en minimisant la perte de données et l’impact sur les autres objets.

## Contexte

- Table impactée : `metier.demandes_rdv`.
- Données concernées :
  - Rendez-vous des citoyens auprès des services municipaux.
- Impacts métiers :
  - Impossibilité de consulter ou de planifier certains rendez-vous.
  - Incohérences dans les écrans ou les rapports.

## Hypothèse d’incident

Plusieurs scénarios possibles :

- Suppression accidentelle d’un volume important de lignes.
- Mise à jour incorrecte d’un ensemble de rendez-vous (champs de date, statut, etc.).
- Corruption logique suite à une opération de charge ou à un bug applicatif.

Dans la maquette, l’incident est simulé par :

- Suppression ou modification massif des données dans `metier.demandes_rdv`.

## Options de restauration

### Option 1 – Restauration ciblée à partir du dump

1. Identifier une sauvegarde récente contenant la table `demandes_rdv`.
2. Extraire uniquement les données de cette table à partir du fichier dump PostgreSQL, en utilisant les options de `pg_restore`.
3. Restaurer la table dans un environnement de test, puis comparer avec la table de production pour préparer une remise à niveau.

Cette option est plus précise mais demande une bonne maîtrise de `pg_restore` et des impacts applicatifs.

### Option 2 – Restauration de la table à partir de la dernière sauvegarde complète

Scénario simplifié :

1. Sauvegarder l’état actuel de la table corrompue dans un environnement de test si nécessaire.
2. Restaurer l’intégralité de la base `mairie` dans un environnement de recette ou sur une base temporaire.
3. Exporter les données de la table `demandes_rdv` depuis l’environnement restauré.
4. Réinjecter ces données dans la base de production, après validation.

Cette option est adaptée à un contexte où les outils sont limités mais demande une coordination étroite avec les équipes métiers.

## Étapes détaillées du scénario

### 1. Détection et qualification

1. Anomalies détectées :
   - Messages d’erreur lors de la consultation des rendez-vous.
   - Incohérences dans les rapports de charge.
2. Analyse :
   - Comparaison du volume de données actuel avec un historique.
   - Vérification des logs applicatifs et des traitements récents.

### 2. Gel des opérations sur la table

1. En accord avec les métiers, suspendre temporairement :
   - Les traitements batch impactant les rendez-vous.
   - Les opérations de modification sur la table, si possible.
2. Consigner l’heure de découverte de l’incident.

### 3. Préparation de la restauration

1. Identifier la dernière sauvegarde valide contenant des données cohérentes pour `demandes_rdv`.
2. Restaurer la base sur un environnement de test via `restore_runner.py`.
3. Contrôler le contenu de la table restaurée dans cet environnement.

### 4. Comparaison et stratégie de remise à niveau

Plusieurs options :

- Remplacement complet de la table :
  - Supprimer les données corrompues sur la base de production.
  - Recharger les données à partir de l’environnement restauré.
- Remise à niveau partielle :
  - Limiter la restauration à une plage de dates ou un périmètre fonctionnel (par exemple, les rendez-vous du mois en cours).
  - Utiliser des scripts d’upsert pour corriger / insérer les lignes.

Le choix dépend :

- De l’ampleur de la corruption.
- De la tolérance métier à la perte ou à la réécriture de données.

### 5. Validation et reprise d’activité

1. Valider avec les métiers :
   - La cohérence des rendez-vous.
   - Le fonctionnement des écrans et des rapports clés.
2. Reprendre progressivement les traitements suspendus.
3. Surveiller les indicateurs techniques et fonctionnels (KPI de charge et de volumétrie).

### 6. Retour d’expérience

1. Documenter l’incident :
   - Origine probable.
   - Durée d’indisponibilité ou de perturbation.
   - Données perdues ou corrigées.
2. Mettre à jour :
   - Les procédures de charge et de contrôle.
   - Les scripts d’audit ou de supervision, si nécessaire.
3. Sensibiliser les équipes sur les manipulations sensibles (scripts massifs, imports, mises à jour manuelles).

## Enseignements du scénario

- L’importance de disposer d’une sauvegarde exploitable et récente.
- L’intérêt d’avoir un environnement de test pour vérifier les données avant remise à niveau.
- La nécessité d’une communication claire avec les métiers lors des opérations de correction de données.
::contentReference[oaicite:0]{index=0}
