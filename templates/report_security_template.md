<!-- templates/report_security_template.md -->

# Rapport d’audit de sécurité des bases de données

Date de génération : {{ generation_datetime }}
Environnement      : {{ environment_name }}

## 1. Synthèse exécutive

- Instances auditées : {{ instances_count }}
- Bases auditées     : {{ databases_count }}
- Anomalies critiques : {{ critical_findings_count }}
- Anomalies majeures  : {{ major_findings_count }}
- Anomalies mineures  : {{ minor_findings_count }}

Résumé :
- {{ summary_line_1 }}
- {{ summary_line_2 }}
- {{ summary_line_3 }}

## 2. Droits excessifs et rôles sensibles

| Base  | Rôle / Utilisateur | Type d’objet | Objet          | Niveau de privilège |
|-------|--------------------|--------------|----------------|---------------------|
{{ excessive_privileges_rows }}

Analyse :
- Comptes ou rôles à risque : {{ excessive_privileges_comment }}
- Actions recommandées      : {{ excessive_privileges_reco }}

## 3. Objets exposés au rôle PUBLIC

| Base  | Schéma   | Objet          | Type  | Commentaire      |
|-------|----------|----------------|-------|------------------|
{{ public_objects_rows }}

Analyse :
- Obj. exposés de manière injustifiée : {{ public_objects_comment }}
- Recommandations                     : {{ public_objects_reco }}

## 4. Comptes inactifs ou orphelins

| Nom compte | Type       | Dernière activité | Commentaire |
|------------|------------|-------------------|-------------|
{{ orphan_users_rows }}

Analyse :
- Comptes à désactiver / supprimer : {{ orphan_users_comment }}
- Plan d’assainissement            : {{ orphan_users_reco }}

## 5. Politique de mots de passe (si applicable)

Résumé des contrôles :

- Expiration configurée          : {{ password_expiry_info }}
- Complexité minimale appliquée  : {{ password_complexity_info }}
- Comptes potentiellement faibles : {{ weak_accounts_count }}

Commentaires :
- {{ password_policy_comment }}

## 6. Protection des sauvegardes

- Répertoire principal sauvegardes : {{ backups_root_dir }}
- Droits d’accès observés          : {{ backups_permissions_info }}
- Risques identifiés               : {{ backups_risks }}
- Recommandations                  : {{ backups_reco }}

## 7. Synthèse des recommandations et priorités

1. Actions immédiates (critique) :
   - {{ action_critique_1 }}
   - {{ action_critique_2 }}

2. Actions à court terme :
   - {{ action_court_terme_1 }}
   - {{ action_court_terme_2 }}

3. Actions structurelles :
   - {{ action_structurelle_1 }}
   - {{ action_structurelle_2 }}

Suivi :
- Responsable du plan d’action : {{ owner_name }}
- Prochaine revue de sécurité  : {{ next_review_date }}
