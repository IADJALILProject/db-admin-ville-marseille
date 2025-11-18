-- Schéma de monitoring PostgreSQL / Airflow
-- Vue par un DBA : santé DB, volumétrie, WAL, locks, bloat, tâches Airflow

SET search_path TO public;

CREATE SCHEMA IF NOT EXISTS monitoring;

------------------------------------------------------------
-- 1. Santé globale de la base
------------------------------------------------------------
CREATE TABLE IF NOT EXISTS monitoring.db_health_status (
  ts                timestamptz NOT NULL DEFAULT now(),
  is_up             boolean     NOT NULL,
  active_sessions   integer,
  waiting_sessions  integer,
  blocking_sessions integer,
  avg_query_ms      numeric,
  db_size_bytes     bigint,
  PRIMARY KEY (ts)
);

CREATE INDEX IF NOT EXISTS idx_db_health_status_ts
  ON monitoring.db_health_status (ts);

------------------------------------------------------------
-- 2. Volumétrie des tables
------------------------------------------------------------
CREATE TABLE IF NOT EXISTS monitoring.table_sizes (
  ts           timestamptz NOT NULL DEFAULT now(),
  schema_name  text        NOT NULL,
  table_name   text        NOT NULL,
  size_bytes   bigint      NOT NULL,
  PRIMARY KEY (ts, schema_name, table_name)
);

CREATE INDEX IF NOT EXISTS idx_table_sizes_ts
  ON monitoring.table_sizes (ts);

------------------------------------------------------------
-- 3. Statut des tâches Airflow
------------------------------------------------------------
CREATE TABLE IF NOT EXISTS monitoring.task_status (
  ts          timestamptz NOT NULL DEFAULT now(),
  dag_id      text        NOT NULL,
  task_id     text        NOT NULL,
  run_id      text        NOT NULL,
  status      text        NOT NULL,   -- success / failed / up_for_retry...
  try_number  integer     NOT NULL,
  details     jsonb,
  PRIMARY KEY (ts, dag_id, task_id, run_id)
);

CREATE INDEX IF NOT EXISTS idx_task_status_dag_task_ts
  ON monitoring.task_status (dag_id, task_id, ts);

-- Horodatage précis de l’exécution (optionnel mais utile pour SLA)
ALTER TABLE monitoring.task_status
  ADD COLUMN IF NOT EXISTS started_at   timestamptz,
  ADD COLUMN IF NOT EXISTS finished_at  timestamptz,
  ADD COLUMN IF NOT EXISTS duration_seconds numeric;

------------------------------------------------------------
-- 4. Activité WAL
------------------------------------------------------------
CREATE TABLE IF NOT EXISTS monitoring.wal_activity (
    ts               timestamptz NOT NULL DEFAULT now(),
    wal_lsn          pg_lsn,
    wal_bytes_total  numeric,
    wal_segment_size integer,
    notes            text
);

CREATE INDEX IF NOT EXISTS idx_wal_activity_ts
  ON monitoring.wal_activity (ts);

------------------------------------------------------------
-- 5. Locks / contentions
------------------------------------------------------------
CREATE TABLE IF NOT EXISTS monitoring.lock_events (
    ts       timestamptz NOT NULL DEFAULT now(),
    pid      integer,
    locktype text,
    relation text,
    mode     text,
    granted  boolean,
    query    text
);

CREATE INDEX IF NOT EXISTS idx_lock_events_ts
  ON monitoring.lock_events (ts);

------------------------------------------------------------
-- 6. Bloat des tables métier
------------------------------------------------------------
CREATE TABLE IF NOT EXISTS monitoring.table_bloat (
    ts          timestamptz NOT NULL DEFAULT now(),
    schema_name text,
    table_name  text,
    est_rows    bigint,
    dead_rows   bigint,
    dead_pct    numeric
);

CREATE INDEX IF NOT EXISTS idx_table_bloat_ts
  ON monitoring.table_bloat (ts);
