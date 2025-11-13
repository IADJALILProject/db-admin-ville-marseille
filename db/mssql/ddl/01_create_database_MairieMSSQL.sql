-- mssql/ddl/01_create_database_MairieMSSQL.sql

IF NOT EXISTS (SELECT 1 FROM sys.databases WHERE name = N'MairieMSSQL')
BEGIN
    CREATE DATABASE MairieMSSQL;
END;
GO
