# Sécurité et droits d’accès aux bases de données

## Principes généraux

La sécurité des bases de données repose sur les principes suivants :

- Confidentialité des données.
- Intégrité des informations.
- Disponibilité des services.
- Traçabilité des actions.

L’administration des droits doit systématiquement appliquer le principe du moindre privilège.

## Modèle de rôles

Pour la base principale, un modèle simplifié peut être mis en place :

- Rôle d’administration (`role_admin_bd`)
  - Gestion des schémas, des objets et des comptes.
  - Accès complet à la base à des fins techniques.
- Rôle d’exploitation (`role_exploitation`)
  - Accès en lecture étendue pour les contrôles techniques et les rapports.
- Rôles métiers (`role_service_xxx`)
  - Accès en lecture/écriture restreint à certaines tables ou vues.
  - Filtrage éventuel par arrondissement ou service.

Les privilèges sont accordés aux rôles, puis les utilisateurs sont rattachés aux rôles selon leur fonction.

## Droits d’accès applicatifs

Les applications ne doivent pas se connecter avec des comptes à privilèges élevés. Pour chaque application :

- Créer un utilisateur dédié avec des droits limités aux objets nécessaires.
- Privilégier l’accès via des vues ou des fonctions, plutôt qu’aux tables brutes.
- Limiter les actions possibles (lecture seule pour certains usages).

## Contrôle d’accès aux données sensibles

Certaines données (identité des citoyens, informations de contact, éléments sensibles) nécessitent :

- Un filtrage des accès :
  - Utilisation de vues restreignant les colonnes exposées.
  - Application de filtres par contexte (par exemple, arrondissement).
- Un suivi des accès :
  - Activation de journaux d’audit lorsque cela est possible.
  - Revue régulière des comptes ayant accès aux données sensibles.

## Audits et contrôles

Des scripts d’audit SQL permettent de contrôler régulièrement :

- Les privilèges accordés aux rôles et utilisateurs.
- La présence de comptes inactifs.
- L’existence d’objets accessibles par des rôles trop larges (par exemple `PUBLIC`).
- La cohérence des droits avec la politique de sécurité définie.

Le script `security_audit.py` orchestre l’exécution de ces contrôles et génère un rapport synthétique.

## Protection des sauvegardes

Les sauvegardes contiennent l’intégralité des données, y compris les plus sensibles. Elles doivent :

- Être stockées sur des supports à accès limité.
- Ne pas être accessibles en lecture aux comptes non autorisés.
- Faire l’objet d’une politique de rétention maîtrisée.
- Le cas échéant, être chiffrées en fonction du niveau de sensibilité.

## Documentation et mise à jour

La politique de sécurité doit être documentée et mise à jour en fonction :

- Des évolutions réglementaires.
- Des nouvelles applications ou cas d’usage.
- Des retours d’expérience suite à des audits ou incidents.

Toute modification des droits structurants doit être consignée et, si possible, versionnée.
