-- mssql/maintenance/22_long_running_queries.sql

USE MairieMSSQL;
GO

SELECT
    SYSDATETIME()                              AS date_rapport,
    s.session_id,
    r.status,
    r.start_time,
    DATEDIFF(SECOND, r.start_time, SYSDATETIME()) AS duree_seconds,
    r.command,
    t.text                                     AS requete,
    DB_NAME(r.database_id)                     AS database_name,
    r.wait_type,
    r.wait_time,
    r.blocking_session_id,
    r.cpu_time,
    r.logical_reads
FROM sys.dm_exec_requests AS r
JOIN sys.dm_exec_sessions AS s
    ON r.session_id = s.session_id
CROSS APPLY sys.dm_exec_sql_text(r.sql_handle) AS t
WHERE s.is_user_process = 1
  AND r.start_time IS NOT NULL
  AND DATEDIFF(MINUTE, r.start_time, SYSDATETIME()) > 5
ORDER BY duree_seconds DESC;
GO
