# Bonnes pratiques d’administration des bases de données

## Organisation des schémas et des objets

- Séparer les schémas de référentiel, métier et reporting.
- Adopter des conventions de nommage claires pour les tables, vues, index et contraintes.
- Documenter la finalité de chaque schéma et des principales tables.
- Éviter les accès directs aux tables métiers depuis les outils externes, privilégier des vues dédiées.

## Gestion des comptes et des rôles

- Ne jamais utiliser les comptes super-utilisateurs pour les usages applicatifs.
- Créer des rôles par profil :
  - Rôle d’administration.
  - Rôle d’exploitation (lecture étendue).
  - Rôles métiers (lecture/écriture limitées).
- Accorder les privilèges aux rôles, puis ajouter les utilisateurs aux rôles.
- Utiliser autant que possible des mécanismes de filtrage par ligne (RLS) pour les données sensibles.

## Sauvegardes et restauration

- Définir une politique de sauvegarde adaptée aux besoins métier :
  - Sauvegarde complète régulière.
  - Sauvegarde différentielle ou incrémentale si pertinent.
- Documenter les procédures de restauration correspondantes.
- Tester régulièrement les scénarios de restauration (au minimum en environnement de recette).
- Surveiller l’espace disque dédié aux sauvegardes.

## Performance et maintenance

- Mettre en place des routines de maintenance de base :
  - Analyse et mise à jour des statistiques.
  - Nettoyage et réorganisation des tables si nécessaire.
- Surveiller les requêtes longues ou fréquemment exécutées.
- Analyser l’usage des index et supprimer ceux qui ne sont pas utilisés.
- Prévoir des limites raisonnables sur les connexions et la consommation de ressources.

## Sécurité et conformité

- Appliquer le principe du moindre privilège.
- Contrôler régulièrement les utilisateurs inactifs et les privilèges excessifs.
- Sécuriser les fichiers de configuration et les répertoires de données.
- Mettre en place des audits réguliers d’accès et de configuration.
- Protéger les sauvegardes (droits système, chiffrement si nécessaire).

## Automatisation et traçabilité

- Centraliser la configuration des environnements (fichiers YAML, Ansible, etc.).
- Versionner les scripts SQL et Python dans un dépôt Git.
- Associer des logs aux scripts automatisés (fichiers de log, rotation, niveaux de log).
- Documenter les procédures d’exécution et de reprise.

## Supervision et reporting

- Exposer des métriques de base :
  - Disponibilité des instances.
  - Temps de réponse moyen de certaines requêtes.
  - Volumétrie des bases et des tables critiques.
- Définir des indicateurs et seuils d’alerte cohérents avec les attentes métiers.
- Produire des rapports réguliers (hebdomadaires ou mensuels) sur l’état des bases de données.
