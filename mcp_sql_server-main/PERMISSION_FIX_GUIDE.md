# SQL Server Permission Fix Guide

## Problem
You're getting this error when trying to drop tables:
```
Cannot drop the table 'Customers', because it does not exist or you do not have permission.
```

This happens because your Windows user doesn't have DROP TABLE permissions in the `master` database.

## Quick Check
Run this to see your current permissions:
```bash
python check_permissions.py
```

## Solution Options

### Option 1: Grant Permissions (Recommended for Development)

1. Open **SQL Server Management Studio (SSMS)** as Administrator
2. Connect to your SQL Server instance (localhost:50998)
3. Open a **New Query** window
4. Run this command to find your username:
   ```sql
   SELECT SYSTEM_USER;
   ```
5. Grant DDL permissions (replace `DOMAIN\Username` with your actual username):
   ```sql
   USE master;
   EXEC sp_addrolemember 'db_ddladmin', 'DOMAIN\Username';
   ```

The `db_ddladmin` role allows:
- CREATE TABLE
- ALTER TABLE
- DROP TABLE
- All DDL operations

### Option 2: Use a Different Database (Easier)

Instead of using the `master` database, create your own:

1. Open SSMS and run:
   ```sql
   CREATE DATABASE TestDB;
   USE TestDB;
   EXEC sp_addrolemember 'db_owner', 'DOMAIN\Username';
   ```

2. Update your `.env` file:
   ```
   MSSQL_DATABASE=TestDB
   ```

3. Restart the API server:
   ```bash
   python run_api.py
   ```

### Option 3: Run SQL Server with Full Admin Rights

If you're running SQL Server Express locally for development:

1. Stop SQL Server service
2. Start it with your Windows account as sysadmin
3. Or connect using SQL Server Authentication with sa account

## Verify Permissions

After granting permissions, verify they work:

```bash
python check_permissions.py
```

You should see:
```
CREATE TABLE: ✓ Allowed
ALTER TABLE:  ✓ Allowed
DROP TABLE:   ✓ Allowed
```

## Test DROP TABLE

Once permissions are granted, test with:

**Request:**
```json
{
  "query": "Drop the Customers table"
}
```

**Expected Response:**
```json
{
  "success": true,
  "message": "Table dropped successfully"
}
```

## Common Issues

### Issue: "User does not exist"
- Make sure you're using the exact Windows username format
- Check with: `SELECT SYSTEM_USER;` in SSMS

### Issue: Still getting permission errors
- You might need to reconnect to SQL Server
- Restart your API server: `python run_api.py`
- Permissions take effect on new connections

### Issue: Can't connect to SSMS
- Make sure SQL Server Express is running
- Check Windows Services for "SQL Server (SQLEXPRESS)"
- Verify port 50998 is correct

## Best Practice for Development

For development work, it's better to:
1. Create a dedicated test database (not `master`)
2. Grant `db_owner` role to your user in that database
3. Keep `master` database protected

This way you have full control in your test database without risking the system database.
