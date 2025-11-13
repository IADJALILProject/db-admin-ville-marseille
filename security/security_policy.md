# Politique d’accès aux bases de données – Ville de Marseille

## 1. Principes généraux

La politique d’accès aux bases de données repose sur les principes suivants :

- Application stricte du principe du moindre privilège.
- Séparation claire des rôles techniques et métiers.
- Traçabilité des actions d’administration et d’exploitation.
- Protection renforcée des données à caractère personnel.

Les droits sont accordés en priorité à des **rôles**. Les comptes utilisateurs sont ensuite rattachés à ces rôles.

## 2. Typologie des rôles

### 2.1 Rôles techniques

- `role_admin_bd`
  - Administration complète des bases de données métiers.
  - Gestion des schémas, des objets et des comptes.
  - Utilisation réservée aux administrateurs de bases de données.
- `role_exploitation`
  - Lecture étendue des données et des vues de supervision.
  - Utilisé par les équipes d’exploitation pour les contrôles techniques.
- `role_reporting`
  - Accès en lecture seule aux vues de reporting.
  - Utilisation par les équipes de pilotage et de décisionnel.

### 2.2 Rôles métiers

- `role_service_etat_civil`
  - Accès en lecture aux référentiels nécessaires.
  - Accès en lecture/écriture aux demandes d’état civil.
- `role_service_urbanisme`
  - Accès en lecture aux référentiels nécessaires.
  - Accès en lecture/écriture aux demandes d’urbanisme.
- `role_service_accueil`
  - Accès en lecture aux référentiels et aux citoyens.
  - Accès en lecture/écriture aux demandes de rendez-vous.

### 2.3 Rôle applicatif

- `role_app_portail_citoyen`
  - Accès restreint aux données du citoyen connecté, via des politiques de sécurité au niveau ligne (RLS).
  - Utilisé par l’application portail citoyen pour exposer les données personnelles de manière sécurisée.

## 3. Utilisateurs et rattachement aux rôles

Les comptes techniques suivants sont définis :

- `dba_marseille`
  - Compte d’administration BD principal.
  - Membre de `role_admin_bd`.
- `exploit_marseille`
  - Compte utilisé par l’exploitation pour les contrôles et scripts.
  - Membre de `role_exploitation`.
- `reporting_marseille`
  - Compte utilisé par les outils de reporting.
  - Membre de `role_reporting`.
- `app_portail_citoyen`
  - Compte technique de l’application portail citoyen.
  - Membre de `role_app_portail_citoyen`.

Les comptes nominatifs des agents sont créés séparément et rattachés aux rôles métier (`role_service_etat_civil`, `role_service_urbanisme`, `role_service_accueil`) en fonction de leurs fonctions.

## 4. Règles d’accès aux schémas et objets

- Schémas `referentiel` et `metier`
  - Accès complet (lecture/écriture) pour `role_admin_bd`.
  - Lecture pour `role_exploitation`.
  - Lecture limitée pour les rôles métiers sur les tables nécessaires.
- Schéma `reporting`
  - Accès complet pour `role_admin_bd`.
  - Lecture pour `role_exploitation` et `role_reporting`.
  - Lecture sélective pour `role_app_portail_citoyen` via des vues dédiées.

Les privilèges sont accordés au niveau des tables, vues et séquences en cohérence avec cette répartition.

## 5. Données personnelles et RLS

Les données personnelles des citoyens sont stockées dans `metier.citoyens` et dans les tables de demandes associées.

Pour l’accès via le portail citoyen :

- Les tables `metier.citoyens`, `metier.demandes_rdv`, `metier.demandes_etat_civil`, `metier.demandes_urbanisme` sont protégées par des politiques de sécurité au niveau ligne.
- Une fonction `metier.current_citoyen_id()` détermine le citoyen concerné en fonction du contexte de session.
- Le rôle `role_app_portail_citoyen` ne peut lire que les enregistrements correspondant au citoyen authentifié.

Cette approche garantit que chaque citoyen ne voit que ses propres données.

## 6. Gestion des comptes et des mots de passe

- Les comptes techniques sont créés avec des mots de passe forts et gérés de manière centralisée.
- Les comptes nominatifs des agents suivent la politique de mot de passe de la collectivité (complexité, renouvellement, historique).
- Aucun compte ne doit rester sans mot de passe lorsque l’authentification par mot de passe est utilisée.
- Les comptes inactifs ou non utilisés sont désactivés puis supprimés après revue.

Des scripts d’audit permettent d’identifier :

- Les comptes potentiellement orphelins.
- Les comptes sans mot de passe.
- Les rôles disposant de privilèges excessifs.

## 7. Accès aux sauvegardes

Les sauvegardes contiennent l’intégralité des données, y compris les données sensibles.

- Les répertoires de sauvegarde sont limités aux comptes techniques autorisés.
- Les droits systèmes sont restreints (`0750` ou plus restrictif).
- En fonction du niveau de sensibilité, un chiffrement des sauvegardes peut être mis en place.
- La consultation des sauvegardes est réservée aux administrateurs BD et, si nécessaire, aux équipes systèmes.

## 8. Supervision et audits

La politique d’accès est complétée par :

- Des audits réguliers des privilèges (scripts SQL dans `security/audits_sql`).
- Des rapports de sécurité générés périodiquement.
- Une revue des comptes et rôles au moins une fois par an, ou après tout projet impactant les droits.

Les résultats des audits donnent lieu à :

- La correction des droits non conformes.
- La mise à jour de la présente politique.
- Des actions de sensibilisation auprès des équipes concernées.

## 9. Mise à jour de la politique

Cette politique doit être révisée :

- Lors de l’ajout de nouvelles applications métiers utilisant les bases de données.
- En cas de modification de l’architecture technique ou des mécanismes d’authentification.
- Suite à des changements réglementaires ou à des recommandations de l’autorité compétente.

Les évolutions significatives doivent être validées par la DSI et, le cas échéant, par les correspondants sécurité et juridiques.
