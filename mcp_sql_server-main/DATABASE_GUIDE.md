# 🗄️ DATABASE USAGE GUIDE

## Understanding Where Your Data Goes

---

## ✅ YES, IT'S YOUR REAL DATABASE!

When you use this system, **ALL queries execute on your actual SQL Server database**.

### Current Configuration:
```
Server: localhost:50998
Database: master
Authentication: Windows Auth
```

**⚠️ IMPORTANT**: Any CREATE, INSERT, UPDATE, DELETE queries will **actually modify your database**!

---

## 🔍 HOW TO CHECK YOUR DATABASE

### Method 1: Use the Database Inspector Script

```bash
python check_database.py
```

**This will show:**
- All tables in your database
- Row counts for each table
- Sample data from each table
- All databases on your server

### Method 2: SQL Server Management Studio (SSMS)

1. Open **SQL Server Management Studio**
2. Connect to: `localhost\SQLEXPRESS`
3. Expand **Databases** → **master** (or your configured database)
4. Expand **Tables**
5. Right-click any table → **Select Top 1000 Rows**

### Method 3: Command Line (sqlcmd)

```bash
sqlcmd -S localhost\SQLEXPRESS -E -Q "SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'"
```

### Method 4: Using Our API

```bash
# Start API
python run_api.py

# Query tables
curl -X POST http://localhost:8000/api/query/text \
  -H "Content-Type: application/json" \
  -d "{\"query\": \"List all tables in my database\"}"
```

---

## 📊 WHAT TABLES ARE CREATED?

### System Tables (Created Automatically):

When you run the POC, these tables are created in your database:

1. **query_history** - Stores all executed queries
2. **query_candidates** - Stores generated SQL candidates
3. **optimization_metrics** - Performance metrics
4. **query_cache** - Cached query results
5. **rl_state** - Reinforcement learning states
6. **q_table** - Q-learning values

### User Tables (Created by You):

Any tables you create through queries will also be in the same database.

---

## 🎯 EXAMPLE: CREATE A TABLE

### Using the API:

```bash
curl -X POST http://localhost:8000/api/query/text \
  -H "Content-Type: application/json" \
  -d "{\"query\": \"Create a table called customers with id, name, and email\"}"
```

### What Happens:

1. System generates SQL:
   ```sql
   CREATE TABLE customers (
       id INT PRIMARY KEY, 
       name VARCHAR(100), 
       email VARCHAR(100)
   )
   ```

2. Executes on your database: `localhost:50998/master`

3. Table is created in the `dbo` schema

### Verify It Was Created:

```bash
# Method 1: Inspector script
python check_database.py

# Method 2: Query via API
curl -X POST http://localhost:8000/api/query/text \
  -H "Content-Type: application/json" \
  -d "{\"query\": \"List all tables\"}"

# Method 3: Direct SQL
sqlcmd -S localhost\SQLEXPRESS -E -Q "SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'customers'"
```

---

## 🔄 EXAMPLE: INSERT DATA

```bash
curl -X POST http://localhost:8000/api/query/text \
  -H "Content-Type: application/json" \
  -d "{\"query\": \"Insert into customers values (1, 'John Doe', 'john@example.com')\"}"
```

### Verify Data:

```bash
curl -X POST http://localhost:8000/api/query/text \
  -H "Content-Type: application/json" \
  -d "{\"query\": \"Select all from customers\"}"
```

---

## 🗑️ CLEANING UP

### Delete a Table:

```bash
curl -X POST http://localhost:8000/api/query/text \
  -H "Content-Type: application/json" \
  -d "{\"query\": \"DROP TABLE customers\"}"
```

### Delete System Tables:

```sql
-- Connect to SQL Server and run:
DROP TABLE IF EXISTS query_history;
DROP TABLE IF EXISTS query_candidates;
DROP TABLE IF EXISTS optimization_metrics;
DROP TABLE IF EXISTS query_cache;
DROP TABLE IF EXISTS rl_state;
DROP TABLE IF EXISTS q_table;
```

---

## 🔒 SAFETY RECOMMENDATIONS

### 1. Use a Test Database

Instead of using `master`, create a test database:

```sql
-- In SSMS or sqlcmd:
CREATE DATABASE test_db;
```

Then update `.env`:
```bash
MSSQL_DATABASE=test_db
```

### 2. Backup Before Testing

```sql
-- Backup your database
BACKUP DATABASE master TO DISK = 'C:\Backup\master_backup.bak';
```

### 3. Use Read-Only Mode (Optional)

Create a read-only user for testing:

```sql
CREATE LOGIN readonly_user WITH PASSWORD = 'YourPassword123!';
CREATE USER readonly_user FOR LOGIN readonly_user;
GRANT SELECT ON DATABASE::master TO readonly_user;
```

Update `.env`:
```bash
MSSQL_USER=readonly_user
MSSQL_PASSWORD=YourPassword123!
MSSQL_WINDOWS_AUTH=false
```

---

## 📍 WHERE IS MY DATA STORED?

### Database Files Location:

Your SQL Server data files are typically at:
```
C:\Program Files\Microsoft SQL Server\MSSQL16.SQLEXPRESS\MSSQL\DATA\
```

Files:
- `master.mdf` - Primary data file
- `master_log.ldf` - Transaction log

### View File Locations:

```sql
SELECT 
    name AS DatabaseName,
    physical_name AS FileLocation
FROM sys.master_files
WHERE database_id = DB_ID('master');
```

---

## 🔍 MONITORING QUERIES

### View Query History:

```sql
SELECT TOP 10 
    original_nl,
    generated_sql,
    execution_time_ms,
    success,
    timestamp
FROM query_history
ORDER BY timestamp DESC;
```

### View What Tables Were Created:

```sql
SELECT 
    TABLE_NAME,
    CREATE_DATE = (
        SELECT create_date 
        FROM sys.tables 
        WHERE name = INFORMATION_SCHEMA.TABLES.TABLE_NAME
    )
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_TYPE = 'BASE TABLE'
AND TABLE_SCHEMA = 'dbo'
ORDER BY CREATE_DATE DESC;
```

---

## 🎯 PRACTICAL EXAMPLES

### Example 1: Create and Use a Test Table

```bash
# 1. Create table
curl -X POST http://localhost:8000/api/query/text \
  -H "Content-Type: application/json" \
  -d "{\"query\": \"Create a table called products with id, name, and price\"}"

# 2. Insert data
curl -X POST http://localhost:8000/api/query/text \
  -H "Content-Type: application/json" \
  -d "{\"query\": \"Insert into products values (1, 'Laptop', 999.99)\"}"

# 3. Query data
curl -X POST http://localhost:8000/api/query/text \
  -H "Content-Type: application/json" \
  -d "{\"query\": \"Select all from products\"}"

# 4. Check in database
python check_database.py

# 5. Clean up
curl -X POST http://localhost:8000/api/query/text \
  -H "Content-Type: application/json" \
  -d "{\"query\": \"DROP TABLE products\"}"
```

### Example 2: View System Metrics

```bash
# Check how many queries were executed
curl -X POST http://localhost:8000/api/query/text \
  -H "Content-Type: application/json" \
  -d "{\"query\": \"SELECT COUNT(*) as total_queries FROM query_history\"}"

# Check cache performance
curl -X POST http://localhost:8000/api/query/text \
  -H "Content-Type: application/json" \
  -d "{\"query\": \"SELECT COUNT(*) as cached_queries FROM query_cache\"}"

# Check RL learning progress
curl -X POST http://localhost:8000/api/query/text \
  -H "Content-Type: application/json" \
  -d "{\"query\": \"SELECT COUNT(*) as learned_states FROM q_table\"}"
```

---

## 🚨 TROUBLESHOOTING

### Issue: "Table already exists"

**Solution**: Table was created in a previous run. Either:
1. Drop it: `DROP TABLE table_name`
2. Use a different name
3. Use `CREATE TABLE IF NOT EXISTS` (SQL Server 2016+)

### Issue: "Cannot find table"

**Solution**: Check which database you're connected to:
```sql
SELECT DB_NAME() AS CurrentDatabase;
```

### Issue: "Permission denied"

**Solution**: Your user doesn't have CREATE/INSERT permissions. Either:
1. Use Windows Auth (has full permissions)
2. Grant permissions to your SQL user
3. Use a different database where you have permissions

---

## 📊 QUICK REFERENCE

| Task | Command |
|------|---------|
| Check database | `python check_database.py` |
| List tables | Query: "List all tables" |
| Create table | Query: "Create table..." |
| Insert data | Query: "Insert into..." |
| View data | Query: "Select from..." |
| Delete table | Query: "DROP TABLE..." |
| View history | `SELECT * FROM query_history` |
| View cache | `SELECT * FROM query_cache` |
| View Q-table | `SELECT * FROM q_table` |

---

## ✅ BEST PRACTICES

1. **Use a test database** - Don't use `master` for testing
2. **Backup regularly** - Before running destructive queries
3. **Check before deleting** - Use `SELECT` before `DELETE`
4. **Monitor query history** - Review what was executed
5. **Clean up test data** - Drop test tables when done

---

**💡 Remember**: This system executes REAL SQL on your REAL database. Always verify what you're doing!
