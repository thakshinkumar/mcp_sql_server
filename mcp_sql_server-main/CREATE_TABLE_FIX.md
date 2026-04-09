# CREATE TABLE Issue - Analysis and Fixes

## What Was Changed

### Issue 1: Missing Autocommit for Table DDL
**Before**: CREATE/DROP DATABASE had autocommit, but CREATE TABLE didn't

**Fixed**: Added autocommit=True for all table DDL operations:
- CREATE TABLE
- DROP TABLE
- ALTER TABLE
- TRUNCATE TABLE

### Issue 2: Poor Error Messages
**Before**: Generic 500 error without details

**Fixed**: Added detailed error logging:
- Table DDL errors logged with "Table DDL Error: " prefix
- Database DDL errors logged with "Database DDL Error: " prefix
- Execution errors logged with "Execution Error: " prefix
- All errors printed to console for debugging

### Issue 3: Missing Transaction Management
**Before**: No rollback on error for table operations

**Fixed**: 
- Added conn.rollback() on error
- Added conn.commit() after successful execution
- Proper try/except/finally blocks for each operation type

## What to Do Next

### Step 1: Restart the API Server
The code changes require a server restart to take effect.

```
$ python -m uvicorn mssql_mcp_server.api.main:app --reload --app-dir src
```

### Step 2: Check Current State
Try this query to see what tables exist:
```
Query: "show all tables"
```

Expected: List of tables in database

### Step 3: Handle Existing Table
If the 'employees' table already exists from failed attempts:

**Option A**: Drop it with a query
```
Query: "drop the employees table"
```
Or:
```
Query: "DROP TABLE employees;"
```

**Option B**: Create with a different name
```
Query: "create a table called employees_new with id, name, and salary"
```

### Step 4: Test CREATE TABLE Again
Once old tables are cleaned up, try:
```
Query: "create a table called employees with id, name, and salary"
```

Expected: Success with message "Table DDL command executed successfully"

## Why CREATE TABLE Was Failing

Most likely causes (in order of probability):
1. **Table already exists** - Table persisted from previous failed attempts
   - SQL Server error: "There is already an object named 'employees' in the database"
   
2. **Missing autocommit** - Same issue as CREATE DATABASE
   - SQL Server might have been in implicit transaction mode
   - Fixed by enabling autocommit like we did for databases

3. **Transaction isolation issue** - Pending transactions blocking DDL
   - Fixed by adding explicit commit/rollback

## Code Changes Made

**File**: `src/mssql_mcp_server/api/main.py`

**Lines 455-476**: Added special handling for table DDL
```python
# Special handling for table DDL (CREATE/DROP/ALTER TABLE) - may need autocommit
if any(sql_upper.startswith(keyword) for keyword in ["CREATE TABLE", "DROP TABLE", "ALTER TABLE", "TRUNCATE TABLE"]):
    original_autocommit = conn.autocommit
    conn.autocommit = True
    try:
        cursor.execute(sql_query)
        conn.commit()
        return {"sql": sql_query, "result": "Table DDL command executed successfully"}
    except Exception as e:
        conn.rollback()
        error_msg = f"Table DDL Error: {str(e)}"
        print(f"ERROR: {error_msg}")
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        conn.autocommit = original_autocommit
```

## Expected Behavior After Fix

✓ Natural language table creation: "create employees table with id, name, salary"
✓ Natural language DROP: "drop the employees table"
✓ Table exists error message will be clear and helpful
✓ Proper transaction handling with commit/rollback
✓ Detailed error logging for debugging

## Test the Fix

After restarting the server:

Test 1: Show all tables (should list what exists)
```
Query: "show all tables"
Expected: List of table names
HTTP: 200 OK
```

Test 2: Create a table
```
Query: "create a table called test_employees with id, name, salary, email"
Expected: Table DDL command executed successfully
HTTP: 200 OK
```

Test 3: Describe the table
```
Query: "describe test_employees"
Expected: List of columns with types
HTTP: 200 OK
```

Test 4: Drop the table
```
Query: "drop the test_employees table"
Expected: Table DDL command executed successfully
HTTP: 200 OK
```

## Debugging Tips

If you still get errors after restarting:

1. **Check the console output** - The error message will show exactly what went wrong
2. **Verify SQL Server is running** - `localhost\SQLEXPRESS` must be accessible
3. **Check permissions** - Your SQL Server login must have DDL permissions on testdb
4. **Look for sql keyword in error** - The actual SQL error from SQL Server will be in the detail
5. **Run "show all tables" first** - This confirms connection works and shows existing tables
