<!-- templates/email_alert_template.md -->

Objet : [ALERTE BDD] {{ severity }} – {{ system_name }} – {{ short_description }}

Bonjour,

Une alerte vient d’être générée par le dispositif de supervision des bases de données.

Informations principales :

- Système      : {{ system_name }}
- Instance     : {{ instance_name }}
- Base         : {{ database_name }}
- Gravité      : {{ severity }}
- Date / heure : {{ event_datetime }}
- Source       : {{ source_component }}

Résumé de l’alerte :

{{ alert_summary }}

Détails techniques :

- Type d’événement : {{ event_type }}
- Code / référence : {{ event_code }}
- Mesure relevée   : {{ measured_value }}
- Seuil attendu    : {{ expected_threshold }}
- Contexte         : {{ technical_context }}

Actions recommandées :

1. {{ action_1 }}
2. {{ action_2 }}
3. {{ action_3 }}

Merci de :

- Qualifier l’incident (réel / faux positif).
- Mettre à jour le journal d’exploitation après traitement.
- Escalader au référent concerné si nécessaire (DBA / système / réseau / applicatif).

Ceci est un message automatique généré par le module de supervision des bases de données.
