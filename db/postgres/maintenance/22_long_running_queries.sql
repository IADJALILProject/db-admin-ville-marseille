-- 22_long_running_queries.sql

SET search_path TO public;

SELECT
    now()::timestamp                       AS date_rapport,
    pid,
    usename                                AS utilisateur,
    datname                                AS base,
    application_name,
    client_addr,
    backend_start,
    query_start,
    now() - query_start                    AS duree,
    state,
    wait_event_type,
    wait_event,
    left(query, 2000)                      AS requete
FROM pg_stat_activity
WHERE state <> 'idle'
  AND query_start IS NOT NULL
  AND now() - query_start > interval '5 minutes'
ORDER BY duree DESC;
