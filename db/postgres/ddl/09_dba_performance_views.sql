-- 09_dba_performance_views.sql
-- Objets DBA pour les dashboards Grafana (Performance & Maintenance)
-- Compatible PostgreSQL 16 (pg_stat_statements 1.10)

-- 1. Extensions nécessaires
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;
CREATE EXTENSION IF NOT EXISTS pgstattuple;

-- 2. Schéma logique pour les vues DBA
CREATE SCHEMA IF NOT EXISTS dba;

--------------------------------------------------------------------------------
-- 3. Top requêtes lentes (pg_stat_statements)
--    NB : en PG16, on utilise total_exec_time / mean_exec_time (en millisecondes)
--------------------------------------------------------------------------------
CREATE OR REPLACE VIEW dba.top_queries AS
SELECT
  query,
  calls,
  round(total_exec_time::numeric, 2) AS total_time_ms,
  round((total_exec_time / NULLIF(calls, 0))::numeric, 2) AS avg_time_ms,
  rows
FROM pg_stat_statements
WHERE dbid = (SELECT oid FROM pg_database WHERE datname = current_database())
ORDER BY avg_time_ms DESC
LIMIT 50;

--------------------------------------------------------------------------------
-- 4. Tables avec le plus d’I/O (pg_statio_user_tables)
--------------------------------------------------------------------------------
CREATE OR REPLACE VIEW dba.table_io AS
SELECT
  schemaname,
  relname AS table_name,
  heap_blks_read + heap_blks_hit + idx_blks_read + idx_blks_hit AS total_io,
  heap_blks_read,
  heap_blks_hit,
  idx_blks_read,
  idx_blks_hit
FROM pg_statio_user_tables
ORDER BY total_io DESC
LIMIT 50;

--------------------------------------------------------------------------------
-- 5. Tables les plus volumineuses
--------------------------------------------------------------------------------
CREATE OR REPLACE VIEW dba.table_size AS
SELECT
  n.nspname AS schema_name,
  c.relname AS table_name,
  pg_total_relation_size(c.oid) AS total_bytes,
  pg_relation_size(c.oid)       AS table_bytes,
  pg_indexes_size(c.oid)        AS index_bytes
FROM pg_class c
JOIN pg_namespace n ON n.oid = c.relnamespace
WHERE c.relkind = 'r'
ORDER BY total_bytes DESC
LIMIT 50;

--------------------------------------------------------------------------------
-- 6. Index jamais / peu utilisés
--------------------------------------------------------------------------------
CREATE OR REPLACE VIEW dba.unused_indexes AS
SELECT
  s.schemaname,
  s.relname      AS table_name,
  s.indexrelname AS index_name,
  s.idx_scan,
  pg_size_pretty(pg_relation_size(s.indexrelid)) AS index_size
FROM pg_stat_user_indexes s
JOIN pg_index i ON i.indexrelid = s.indexrelid
WHERE s.idx_scan < 10
  AND i.indisunique = FALSE
  AND i.indisprimary = FALSE
ORDER BY s.idx_scan ASC, pg_relation_size(s.indexrelid) DESC
LIMIT 100;

--------------------------------------------------------------------------------
-- 7. Tables très scannées en séquentiel
--------------------------------------------------------------------------------
CREATE OR REPLACE VIEW dba.seq_scan_tables AS
SELECT
  schemaname,
  relname AS table_name,
  seq_scan,
  idx_scan,
  n_tup_ins,
  n_tup_upd,
  n_tup_del,
  n_live_tup,
  n_dead_tup
FROM pg_stat_user_tables
WHERE seq_scan > 0
ORDER BY seq_scan DESC
LIMIT 100;

--------------------------------------------------------------------------------
-- 8. Locks / contentions en cours
--------------------------------------------------------------------------------
CREATE OR REPLACE VIEW dba.current_locks AS
SELECT
  now() AS "time",
  a.datname,
  a.pid,
  a.usename,
  a.application_name,
  a.client_addr,
  l.relation::regclass AS relation,
  l.mode,
  l.granted,
  a.state,
  a.query,
  a.query_start
FROM pg_locks l
JOIN pg_stat_activity a ON a.pid = l.pid
WHERE a.datname = current_database()
ORDER BY l.granted ASC, a.query_start DESC;

--------------------------------------------------------------------------------
-- 9. Statut VACUUM / AUTOVACUUM
--------------------------------------------------------------------------------
CREATE OR REPLACE VIEW dba.vacuum_status AS
SELECT
  schemaname,
  relname,
  n_tup_ins,
  n_tup_upd,
  n_tup_del,
  n_live_tup,
  n_dead_tup,
  last_vacuum,
  last_autovacuum,
  last_analyze,
  last_autoanalyze
FROM pg_stat_all_tables
WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
ORDER BY n_dead_tup DESC
LIMIT 100;
