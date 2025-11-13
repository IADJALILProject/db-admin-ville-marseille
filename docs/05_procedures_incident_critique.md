# Procédures en cas d’incident critique

## Objectif

Fournir un cadre pour la gestion des incidents majeurs affectant les bases de données, en limitant l’impact sur les services et en garantissant une remise en service maîtrisée.

## Typologie des incidents

Les incidents critiques incluent, sans s’y limiter :

- Indisponibilité totale d’une instance de base de données.
- Corruption avérée d’une base ou d’une table critique.
- Perte ou suppression accidentelle de données.
- Performances fortement dégradées impactant la continuité de service.
- Incident de sécurité (accès non autorisé, fuite potentielle de données).

## Étapes générales de gestion d’incident

1. Détection
   - Incident détecté via alerte de supervision, appel d’un service métier ou analyse manuelle.
2. Qualification
   - Identifier la nature de l’incident (fonctionnel, technique, sécurité).
   - Estimer l’impact (services affectés, périmètre fonctionnel).
3. Communication
   - Informer le responsable d’astreinte ou le référent BD.
   - Informer les interlocuteurs métier concernés si nécessaire.
4. Stabilisation
   - Arrêter les traitements aggravants si nécessaire (batchs, chargements).
   - Mettre en place des mesures conservatoires (blocage d’accès, bascule éventuelle).

## Restauration et résolution

Selon la nature de l’incident :

- Indisponibilité d’instance
  - Redémarrer l’instance en respectant les procédures du SGBD.
  - En cas d’échec, appliquer la procédure de restauration à partir de la dernière sauvegarde valide.
- Corruption de données
  - Identifier le périmètre de la corruption (tables, schémas).
  - Restauration ciblée depuis une sauvegarde ou rechargement à partir de la source de vérité (fichiers ou systèmes externes).
- Incident de performance
  - Analyser les métriques (temps de requête, verrous, consommation de ressources).
  - Identifier les requêtes ou opérations problématiques.
  - Appliquer les actions correctives (index, optimisation, reconfiguration).

Les scripts `restore_runner.py` et les scénarios de `tests/scenarios_pra` servent de base pour les procédures de restauration.

## Clôture et retour d’expérience

Après résolution :

- Vérifier le retour à la normale :
  - Disponibilité des services.
  - Cohérence des données.
  - Stabilité des performances.
- Documenter l’incident :
  - Chronologie des événements.
  - Actions menées, durée de l’interruption.
  - Relation avec les sauvegardes et les tests PRA/PCA.
- Proposer des actions préventives :
  - Améliorations de configuration.
  - Renforcement des contrôles.
  - Mise à jour de la documentation et des procédures.

## Rôles impliqués

- Administrateur de bases de données : pilotage technique de la résolution.
- Équipe systèmes : prise en charge de l’infrastructure, si nécessaire.
- Chefs de projets / référents métier : information et validation du rétablissement de service.
- Responsable de la DSI : arbitrage en cas de choix de restauration impactant plusieurs services.
