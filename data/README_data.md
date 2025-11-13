# Données du projet – Contexte Ville de Marseille

Ce répertoire contient les données brutes utilisées pour simuler le contexte d’une mairie comme la Ville de Marseille. Elles alimentent les bases de données PostgreSQL/MySQL/MSSQL et servent de base aux scripts d’administration, de supervision et d’analyse.

## Structure du dossier `data/`

- `data/sources/`
  - Données brutes simulant les systèmes métiers (citoyens, services, demandes, rendez-vous).
- `data/generated/`
  - Données dérivées et agrégées, générées à partir des sources (enrichissements, agrégats quotidiens, vues d’analyse).

## Fichiers de `data/sources/`

### `citoyens.csv`

Liste de citoyens domiciliés à Marseille.

Champs principaux :

- `citoyen_id` : identifiant unique du citoyen.
- `nom` : nom de famille.
- `prenom` : prénom.
- `date_naissance` : date de naissance (AAAA-MM-JJ).
- `email` : adresse e-mail de contact.
- `telephone` : numéro de téléphone.
- `adresse` : adresse postale.
- `code_postal` : code postal, dans la plage 13001–13016.
- `ville` : ville de résidence (Marseille).
- `arrondissement` : arrondissement (1e à 16e).

Utilisation :

- Base de référence pour les relations avec les services municipaux.
- Point de départ pour l’enrichissement des profils dans `citoyens_enrichis.csv`.

---

### `services_municipaux.csv`

Référentiel des services de la mairie et de leurs implantations.

Champs principaux :

- `service_id` : identifiant unique du service.
- `code_service` : code fonctionnel (ETAT_CIVIL, URBANISME, etc.).
- `nom_service` : libellé du service.
- `type_service` : catégorie de service (Etat civil, Urbanisme, Social…).
- `arrondissement` : arrondissement de rattachement.
- `email_contact` : contact e-mail du service.
- `telephone_contact` : téléphone du service.

Utilisation :

- Référentiel fonctionnel pour lier les demandes et rendez-vous à un service.
- Base pour des agrégations par service, type de service ou arrondissement.

---

### `demandes_rdv.csv`

Demandes et rendez-vous pris par les citoyens auprès des services municipaux.

Champs principaux :

- `rdv_id` : identifiant unique du rendez-vous.
- `citoyen_id` : lien vers `citoyens.citoyen_id`.
- `service_id` : lien vers `services_municipaux.service_id`.
- `type_rdv` : type de rendez-vous (Etat civil, Urbanisme, etc.).
- `date_demande` : date de la demande de rendez-vous.
- `date_rdv` : date du rendez-vous planifié.
- `statut` : statut (EN_ATTENTE, CONFIRME, HONORE, ANNULE).
- `canal` : canal de prise de rendez-vous (EN_LIGNE, TELEPHONE, GUICHET).
- `commentaire` : commentaire libre.

Utilisation :

- Analyse de la charge des services.
- Calcul des délais entre demande et rendez-vous.
- Base pour les slots planifiés dans `rdv_planifies.csv`.

---

### `demandes_etat_civil.csv`

Demandes de documents d’état civil.

Champs principaux :

- `demande_id` : identifiant unique de la demande.
- `citoyen_id` : lien vers `citoyens.citoyen_id`.
- `type_demande` : type de document demandé (ACTE_NAISSANCE, ACTE_MARIAGE, etc.).
- `date_demande` : date de la demande.
- `date_traitement` : date de traitement.
- `statut` : statut (ENREGISTREE, EN_COURS, TERMINEE, REFUSEE).
- `mode_retrait` : mode de retrait (COURRIER, GUICHET, EN_LIGNE).

Utilisation :

- Suivi des volumes et délais de traitement.
- Statistiques par type de demande d’état civil.

---

### `demandes_urbanisme.csv`

Demandes liées à l’urbanisme (permis, déclarations, autorisations).

Champs principaux :

- `demande_id` : identifiant unique de la demande.
- `citoyen_id` : lien vers `citoyens.citoyen_id`.
- `type_demande` : type de demande (PERMIS_CONSTRUIRE, DECLARATION_PREALABLE, etc.).
- `adresse_projet` : adresse du projet.
- `code_postal` : code postal du projet.
- `arrondissement` : arrondissement du projet.
- `date_demande` : date de dépôt de la demande.
- `date_decision` : date de décision.
- `statut` : statut (ENREGISTREE, INSTRUCTION, ACCEPTEE, REFUSEE).

Utilisation :

- Analyse de la charge sur les services d’urbanisme.
- Suivi des délais d’instruction.
- Cartographie des projets par arrondissement.

---

## Fichiers de `data/generated/`

Les fichiers de `data/generated/` sont construits à partir des sources, par les scripts Python dédiés :

- `citoyens_enrichis.csv` :
  - Profil enrichi des citoyens (nombre de rendez-vous, nombre de demandes, dernier contact, segment d’activité, probabilités de contact par canal, etc.).

- `rdv_planifies.csv` :
  - Vue détaillée des rendez-vous planifiés avec slot horaire, durée, pic horaire ou non, délai entre demande et rendez-vous.

- `stats_quotidiennes.csv` :
  - Agrégats journaliers (volumes de rendez-vous, demandes d’état civil, demandes d’urbanisme, nombre de citoyens distincts).

Ces données dérivées servent de base à :

- L’analyse de charge et de performance perçue par les citoyens.
- La supervision des tendances (pics de demande, saturation de créneaux).
- Des exemples de reporting opérationnel et stratégique.

---

## Génération et régénération des données

Les fichiers de `data/sources/` sont générés par un script Python de simulation. Les fichiers de `data/generated/` sont produits par un second script qui enrichit et agrège les données.

Pour régénérer intégralement les données :

1. Lancer le script de génération des sources pour recréer les CSV bruts dans `data/sources/`.
2. Lancer le script d’enrichissement et d’agrégation pour produire les CSV dans `data/generated/`.

Ces scripts peuvent être rejoués autant que nécessaire pour adapter les volumes ou tester différents scénarios de charge.
