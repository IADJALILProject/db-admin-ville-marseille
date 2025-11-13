<!-- templates/report_perf_template.md -->

# Rapport de performance des bases de données

Date de génération : {{ generation_datetime }}
Période analysée   : {{ period_description }}

## 1. Synthèse exécutive

- Instances analysées        : {{ instances_count }}
- Bases de données analysées : {{ databases_count }}
- Taille totale estimée      : {{ total_size_pretty }}
- Principales observations   :
  - {{ observation_1 }}
  - {{ observation_2 }}
  - {{ observation_3 }}

## 2. Volumétrie des principales tables

Top 10 des tables par taille (toutes bases confondues) :

| Schéma   | Table         | Taille totale | Taille données | Taille index | Lignes estimées |
|----------|---------------|---------------|----------------|--------------|-----------------|
{{ table_sizes_rows }}

Commentaire :
- Tables les plus volumineuses : {{ largest_tables_comment }}
- Recommandations éventuelles : {{ largest_tables_reco }}

## 3. Sessions et activité

- Nombre de sessions actives moyen : {{ avg_sessions }}
- Nombre de sessions actives max   : {{ max_sessions }}
- Verrous identifiés (locks)       : {{ locks_summary }}

Commentaires :
- Charge globale : {{ load_comment }}
- Risques identifiés : {{ load_risks }}

## 4. Requêtes longues ou coûteuses

Critère retenu : durée > {{ long_query_threshold }}

| Base     | Utilisateur | Durée          | Etat   | Extrait requête         |
|----------|------------|----------------|--------|--------------------------|
{{ long_queries_rows }}

Analyse :
- Types d’opérations les plus coûteuses : {{ long_queries_comment }}
- Pistes d’optimisation : {{ long_queries_reco }}

## 5. Utilisation des index

| Schéma   | Table         | Index              | Taille index | Statut                   |
|----------|---------------|--------------------|--------------|--------------------------|
{{ index_usage_rows }}

Interprétation :
- Index potentiellement inutiles : {{ unused_indexes_count }}
- Index jamais utilisés          : {{ never_used_indexes_count }}
- Recommandations d’actions      : {{ index_reco }}

## 6. Synthèse des recommandations

1. Volumétrie
   - {{ reco_volumetrie_1 }}
   - {{ reco_volumetrie_2 }}

2. Requêtes
   - {{ reco_queries_1 }}
   - {{ reco_queries_2 }}

3. Indexation
   - {{ reco_index_1 }}
   - {{ reco_index_2 }}

4. Plan d’action proposé
   - Priorité 1 : {{ action_p1 }}
   - Priorité 2 : {{ action_p2 }}
   - Priorité 3 : {{ action_p3 }}
