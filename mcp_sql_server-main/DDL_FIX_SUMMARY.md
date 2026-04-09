# DDL Statement Success Fix

## Problem
DDL statements (CREATE TABLE, ALTER TABLE, DROP TABLE) were executing successfully and creating/modifying tables, but the API response showed `"success": false`. This was confusing because the operations actually worked.

## Root Cause
The issue was in the execution flow:

1. `cost_evaluator.evaluate_query()` executes the DDL statement (e.g., CREATE TABLE Mobile)
2. The table is created successfully ✓
3. `cost_evaluator` tries to get execution plan by executing the query again
4. Second execution fails because table already exists ✗
5. Response shows `success: false` even though table was created

## Solution
Made two key changes:

### 1. Cost Evaluator (`src/mssql_mcp_server/optimizer/cost_evaluator.py`)
- Detect DDL statements (CREATE, ALTER, DROP, TRUNCATE, RENAME)
- Skip execution plan analysis for DDL (only do it for SELECT queries)
- Skip statistics collection for DDL statements
- Use execution time as cost metric for DDL

### 2. Orchestrator (`src/mssql_mcp_server/orchestrator.py`)
- Don't re-execute DDL/DML queries after cost evaluation
- Only re-execute SELECT queries to fetch result rows
- For DDL/DML, use the result from cost_evaluator directly

## Changes Made

**File: `src/mssql_mcp_server/optimizer/cost_evaluator.py`**
- Added DDL detection: `is_ddl = any(query_upper.startswith(cmd) for cmd in ['CREATE', 'ALTER', 'DROP', 'TRUNCATE', 'RENAME'])`
- Conditional statistics: Only enable for non-DDL queries
- Conditional execution plan: Only for SELECT queries
- Simplified cost calculation for DDL

**File: `src/mssql_mcp_server/orchestrator.py`**
- Separated SELECT query handling from DDL/DML
- SELECT queries: Re-execute to fetch rows
- DDL/DML queries: Use result from cost_evaluator (already executed)
- No double execution of DDL statements

## Testing

Restart the API server:
```bash
python run_api.py
```

Run the test script:
```bash
python test_ddl_fix.py
```

Or test manually:

**Test 1: CREATE TABLE**
```json
{"query": "Create a table called Products with id and name"}
```
Expected: `"success": true`, table created

**Test 2: ALTER TABLE**
```json
{"query": "Add price column to Products table"}
```
Expected: `"success": true`, column added

**Test 3: DROP TABLE**
```json
{"query": "Drop the Products table"}
```
Expected: `"success": true`, table dropped

## Result
Now DDL statements correctly return:
- `"success": true` when operation succeeds
- `"result": {"message": "Query executed successfully. Rows affected: X"}`
- No false errors about objects already existing
