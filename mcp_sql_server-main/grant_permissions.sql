-- SQL Server Permission Grant Script
-- Run this script as Administrator (sa or sysadmin role)

-- Option 1: Grant specific permissions to current Windows user
-- Replace 'DOMAIN\Username' with your actual Windows username
-- To find your username, run: SELECT SYSTEM_USER

-- Grant CREATE TABLE permission
GRANT CREATE TABLE TO [DOMAIN\Username];

-- Grant ALTER permission on schema
GRANT ALTER ON SCHEMA::dbo TO [DOMAIN\Username];

-- Grant DROP permission (allows dropping tables)
GRANT CONTROL ON SCHEMA::dbo TO [DOMAIN\Username];

-- Option 2: Add user to db_ddladmin role (recommended for development)
-- This gives full DDL permissions (CREATE, ALTER, DROP)
EXEC sp_addrolemember 'db_ddladmin', 'DOMAIN\Username';

-- Option 3: Add user to db_owner role (full control - use with caution)
-- EXEC sp_addrolemember 'db_owner', 'DOMAIN\Username';

-- Verify current user and permissions
SELECT SYSTEM_USER AS CurrentUser;
SELECT * FROM fn_my_permissions(NULL, 'DATABASE');
