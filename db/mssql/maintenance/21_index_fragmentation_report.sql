-- mssql/maintenance/21_index_fragmentation_report.sql

USE MairieMSSQL;
GO

SELECT
    DB_NAME(database_id)             AS database_name,
    OBJECT_SCHEMA_NAME(object_id)    AS schema_name,
    OBJECT_NAME(object_id)           AS table_name,
    i.name                           AS index_name,
    ips.index_type_desc,
    ips.avg_fragmentation_in_percent,
    ips.page_count
FROM sys.dm_db_index_physical_stats(DB_ID(), NULL, NULL, NULL, 'SAMPLED') AS ips
JOIN sys.indexes AS i
    ON ips.object_id = i.object_id
   AND ips.index_id = i.index_id
WHERE ips.page_count > 100
ORDER BY
    ips.avg_fragmentation_in_percent DESC,
    ips.page_count DESC;
GO
