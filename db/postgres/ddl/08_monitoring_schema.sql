SET search_path TO public;

CREATE SCHEMA IF NOT EXISTS monitoring;

CREATE TABLE IF NOT EXISTS monitoring.db_health_status (
  ts              timestamptz NOT NULL DEFAULT now(),
  is_up           boolean     NOT NULL,
  active_sessions integer,
  avg_query_ms    numeric,
  db_size_bytes   bigint,
  waiting_sessions integer,
  blocking_sessions integer
);

CREATE INDEX IF NOT EXISTS idx_db_health_status_ts
  ON monitoring.db_health_status (ts);

CREATE TABLE IF NOT EXISTS monitoring.table_sizes (
  ts           timestamptz NOT NULL DEFAULT now(),
  schema_name  text        NOT NULL,
  table_name   text        NOT NULL,
  size_bytes   bigint      NOT NULL,
  PRIMARY KEY (ts, schema_name, table_name)
);

CREATE TABLE IF NOT EXISTS monitoring.task_status (
  ts          timestamptz NOT NULL DEFAULT now(),
  dag_id      text        NOT NULL,
  task_id     text        NOT NULL,
  run_id      text        NOT NULL,
  status      text        NOT NULL, 
  try_number  integer     NOT NULL,
  details     jsonb,
  PRIMARY KEY (ts, dag_id, task_id, run_id)
);

CREATE INDEX IF NOT EXISTS idx_task_status_dag_task
  ON monitoring.task_status (dag_id, task_id, ts);

ALTER TABLE monitoring.task_status
ADD COLUMN IF NOT EXISTS started_at timestamptz,
ADD COLUMN IF NOT EXISTS finished_at timestamptz,
ADD COLUMN IF NOT EXISTS duration_seconds numeric;

CREATE TABLE IF NOT EXISTS monitoring.wal_activity (
    ts                timestamptz NOT NULL DEFAULT now(),
    wal_lsn           pg_lsn,
    wal_bytes_total   numeric,
    wal_segment_size  integer,
    notes             text
);

CREATE TABLE IF NOT EXISTS monitoring.lock_events (
    ts           timestamptz NOT NULL DEFAULT now(),
    pid          integer,
    locktype     text,
    relation     text,
    mode         text,
    granted      boolean,
    query        text
);


CREATE TABLE IF NOT EXISTS monitoring.table_bloat (
    ts            timestamptz NOT NULL DEFAULT now(),
    schema_name   text,
    table_name    text,
    est_rows      bigint,
    dead_rows     bigint,
    dead_pct      numeric
);
