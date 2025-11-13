-- mssql/maintenance/20_update_statistics.sql

USE MairieMSSQL;
GO

EXEC sp_updatestats;
GO
