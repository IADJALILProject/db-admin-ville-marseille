# Définition des principaux KPI – Bases de données Ville de Marseille

## 1. Disponibilité des instances

- Nom : `kpi_instance_availability`
- Description : Pourcentage de temps où l’instance de base de données est joignable et répond dans un délai acceptable.
- Mode de calcul :
  - Fenêtre : quotidienne, hebdomadaire, mensuelle.
  - Disponibilité = 1 − (temps d’indisponibilité / temps total de la fenêtre).
- Seuils recommandés :
  - Alerte majeure : < 99,0 %.
  - Objectif cible : ≥ 99,5 %.

## 2. Temps de réponse des requêtes clés

- Nom : `kpi_query_response_time`
- Description : Temps de réponse moyen et maximum des requêtes considérées comme critiques (consultation de dossier citoyen, listing de rendez-vous, etc.).
- Mode de calcul :
  - Mesure du temps d’exécution sur un échantillon de requêtes clés.
  - Agrégation sur des fenêtres glissantes (5 min, 1 h, 1 jour).
- Seuils recommandés :
  - Alerte mineure si moyenne > 300 ms.
  - Alerte majeure si moyenne > 800 ms ou si des pics répétés > 2 s.

## 3. Volumétrie des bases et tables

- Nom : `kpi_db_size` et `kpi_table_size`
- Description :
  - Taille totale des bases métiers.
  - Taille des tables principales (citoyens, demandes, rendez-vous, urbanisme).
- Mode de calcul :
  - Extraction de la taille en octets (données + index).
  - Conversion en unités lisibles (Mo, Go).
- Utilisation :
  - Suivi de la croissance.
  - Anticipation des besoins en capacité disque.
  - Identification des tables très volumineuses.

## 4. Nombre de sessions et charge globale

- Nom : `kpi_active_sessions`
- Description : Nombre de sessions actives sur l’instance.
- Mode de calcul :
  - Comptage périodique (toutes les minutes par exemple).
  - Calcul des valeurs moyenne, minimale et maximale.
- Seuils indicatifs :
  - Alerte si le nombre de sessions actives se rapproche de la limite configurée (`max_connections`).
- Utilisation :
  - Détection de pics de charge.
  - Ajustement des paramètres de connexion.

## 5. Verrous et contention

- Nom : `kpi_lock_count`
- Description : Nombre de verrous sur la base et présence éventuelle de blocages.
- Mode de calcul :
  - Comptage des verrous via les vues de statistiques.
  - Détection de verrous bloquants (sessions en attente).
- Utilisation :
  - Identification de requêtes problématiques.
  - Amélioration du plan d’exécution ou des transactions.

## 6. Requêtes longues

- Nom : `kpi_long_running_queries`
- Description : Nombre et détail des requêtes dont la durée dépasse un seuil défini.
- Mode de calcul :
  - Filtrage sur une durée minimale (par exemple 5 minutes).
  - Comptage + liste des requêtes concernées.
- Utilisation :
  - Analyse ciblée des traitements lourds.
  - Priorisation des optimisations (index, planification, refonte de requête).

## 7. Statut des sauvegardes

- Nom : `kpi_backup_status`
- Description : État des dernières sauvegardes et respect des objectifs de rétention.
- Attributs :
  - Date et heure de la dernière sauvegarde.
  - Durée de la sauvegarde.
  - Taille du fichier de sauvegarde.
  - Code retour (succès / échec).
- Seuils :
  - Alerte si aucune sauvegarde valide dans la fenêtre attendue (ex. 24 h).
- Utilisation :
  - Vérification continue de la conformité à la politique de sauvegarde.
  - Déclenchement d’actions correctives.

## 8. Volume quotidien de demandes métiers

- Nom : `kpi_daily_requests`
- Description : Nombre de demandes journalières par grand type (rendez-vous, état civil, urbanisme).
- Mode de calcul :
  - Agrégation des enregistrements par jour et par type de demande.
- Utilisation :
  - Visualisation de la charge métier.
  - Mise en évidence des périodes de pointe (saisonnalité, jours de semaine).
  - Ajustement des ressources (guichets, horaires).

## 9. Citoyens distincts servis

- Nom : `kpi_daily_unique_citizens`
- Description : Nombre de citoyens distincts ayant interagi avec la mairie sur une journée (tous canaux confondus).
- Mode de calcul :
  - Comptage des identifiants citoyens distincts dans les demandes et rendez-vous du jour.
- Utilisation :
  - Indicateur synthétique de la fréquentation.
  - Corrélation avec la charge technique et métiers.

## 10. Indicateurs de qualité de données (optionnel)

- Nom : `kpi_data_quality`
- Description :
  - Taux d’enregistrements incomplets (contacts manquants, adresses non valides).
  - Taux d’incohérences de référentiel.
- Utilisation :
  - Suivi de la qualité des données.
  - Mise en place de plans de correction.

Ces KPI peuvent être alimentés par les fichiers de métriques, les vues de reporting et les exports JSON produits par les scripts d’administration, puis visualisés dans des tableaux de bord de supervision.
::contentReference[oaicite:0]{index=0}
