# 📮 POSTMAN TESTING GUIDE

## Complete Step-by-Step Guide for Testing with Postman

---

## 🚀 STEP 1: START THE API SERVER

Open terminal and run:
```bash
python run_api.py
```

**Wait for:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

**Keep this terminal running!**

---

## 📥 STEP 2: OPEN POSTMAN

1. Open Postman application
2. Click **"New"** → **"HTTP Request"**
3. Or use existing workspace

---

## ✅ TEST 1: HEALTH CHECK

### Request Details:
- **Method:** `GET`
- **URL:** `http://localhost:8000/api/health`

### Steps:
1. Select **GET** from dropdown
2. Enter URL: `http://localhost:8000/api/health`
3. Click **Send**

### Expected Response:
```json
{
  "status": "healthy",
  "database": "connected"
}
```

**Status Code:** `200 OK`

---

## 📊 TEST 2: LIST ALL TABLES (BEFORE)

### Request Details:
- **Method:** `POST`
- **URL:** `http://localhost:8000/api/query/text`
- **Headers:** `Content-Type: application/json`
- **Body:** JSON

### Steps:

1. **Select Method:** `POST`

2. **Enter URL:** `http://localhost:8000/api/query/text`

3. **Set Headers:**
   - Click **Headers** tab
   - Add: `Content-Type` = `application/json`

4. **Set Body:**
   - Click **Body** tab
   - Select **raw**
   - Select **JSON** from dropdown
   - Enter:
   ```json
   {
     "query": "List all tables in my database"
   }
   ```

5. **Click Send**

### Expected Response:
```json
{
  "success": true,
  "input": "List all tables in my database",
  "candidates": [
    "SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE';",
    "SELECT name FROM sys.tables WHERE type = 'U';",
    "..."
  ],
  "selected_sql": "SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE';",
  "result": {
    "columns": ["TABLE_NAME"],
    "rows": [
      ["MSreplication_options"],
      ["spt_fallback_db"],
      ["spt_fallback_dev"],
      ["spt_fallback_usg"],
      ["spt_monitor"]
    ]
  },
  "metrics": {
    "execution_time_ms": 45.23,
    "success": true
  },
  "cached": false,
  "error": null
}
```

**Status Code:** `200 OK`

---

## 🆕 TEST 3: CREATE A NEW TABLE

### Request Details:
- **Method:** `POST`
- **URL:** `http://localhost:8000/api/query/text`
- **Headers:** `Content-Type: application/json`
- **Body:** JSON

### Steps:

1. **Select Method:** `POST`

2. **Enter URL:** `http://localhost:8000/api/query/text`

3. **Set Headers:**
   - `Content-Type` = `application/json`

4. **Set Body (Option A - Natural Language):**
   ```json
   {
     "query": "Create a table called customers with id as integer primary key, name as varchar 100, email as varchar 100, and created_date as datetime"
   }
   ```

   **OR Body (Option B - Direct SQL):**
   ```json
   {
     "query": "CREATE TABLE customers (id INT PRIMARY KEY, name VARCHAR(100), email VARCHAR(100), created_date DATETIME DEFAULT GETDATE())"
   }
   ```

5. **Click Send**

### Expected Response:
```json
{
  "success": true,
  "input": "Create a table called customers...",
  "candidates": [
    "CREATE TABLE customers (id INT PRIMARY KEY, name VARCHAR(100), email VARCHAR(100), created_date DATETIME DEFAULT GETDATE())",
    "CREATE TABLE dbo.customers (id INT IDENTITY(1,1) PRIMARY KEY, name NVARCHAR(100), email NVARCHAR(100), created_date DATETIME2 DEFAULT SYSDATETIME())",
    "..."
  ],
  "selected_sql": "CREATE TABLE customers (id INT PRIMARY KEY, name VARCHAR(100), email VARCHAR(100), created_date DATETIME DEFAULT GETDATE())",
  "result": {
    "message": "Query executed successfully. Rows affected: 0"
  },
  "metrics": {
    "execution_time_ms": 125.45,
    "success": true
  },
  "cached": false,
  "error": null
}
```

**Status Code:** `200 OK`

---

## 📊 TEST 4: LIST ALL TABLES (AFTER)

### Request Details:
Same as TEST 2

### Steps:

1. **Use same request as TEST 2**
2. **Click Send**

### Expected Response:
```json
{
  "success": true,
  "input": "List all tables in my database",
  "candidates": [...],
  "selected_sql": "SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE';",
  "result": {
    "columns": ["TABLE_NAME"],
    "rows": [
      ["customers"],          ← NEW TABLE!
      ["MSreplication_options"],
      ["spt_fallback_db"],
      ["spt_fallback_dev"],
      ["spt_fallback_usg"],
      ["spt_monitor"]
    ]
  },
  "metrics": {
    "execution_time_ms": 38.12,
    "success": true
  },
  "cached": false,
  "error": null
}
```

**You should see "customers" in the list!**

---

## 📝 TEST 5: INSERT DATA INTO TABLE

### Request Details:
- **Method:** `POST`
- **URL:** `http://localhost:8000/api/query/text`
- **Body:**

```json
{
  "query": "Insert into customers values (1, 'John Doe', 'john@example.com', GETDATE())"
}
```

### Expected Response:
```json
{
  "success": true,
  "result": {
    "message": "Query executed successfully. Rows affected: 1"
  },
  "metrics": {
    "execution_time_ms": 45.67,
    "success": true
  }
}
```

---

## 🔍 TEST 6: QUERY THE DATA

### Request Details:
- **Method:** `POST`
- **URL:** `http://localhost:8000/api/query/text`
- **Body:**

```json
{
  "query": "Select all from customers"
}
```

### Expected Response:
```json
{
  "success": true,
  "result": {
    "columns": ["id", "name", "email", "created_date"],
    "rows": [
      [1, "John Doe", "john@example.com", "2026-02-16 01:15:30.123"]
    ]
  },
  "metrics": {
    "execution_time_ms": 23.45,
    "success": true
  }
}
```

---

## 📈 TEST 7: GET SYSTEM STATISTICS

### Request Details:
- **Method:** `GET`
- **URL:** `http://localhost:8000/api/stats`

### Steps:
1. Select **GET**
2. Enter URL: `http://localhost:8000/api/stats`
3. Click **Send**

### Expected Response:
```json
{
  "success": true,
  "stats": {
    "cache": {
      "hits": 2,
      "misses": 5,
      "hit_rate": 0.2857,
      "size": 5,
      "max_size": 1000
    },
    "rl_agent": {
      "enabled": true,
      "total_updates": 5,
      "explorations": 1,
      "exploitations": 4,
      "epsilon": 0.095,
      "q_table_size": 3
    },
    "initialized": true
  }
}
```

---

## 🗑️ TEST 8: DELETE THE TABLE (CLEANUP)

### Request Details:
- **Method:** `POST`
- **URL:** `http://localhost:8000/api/query/text`
- **Body:**

```json
{
  "query": "DROP TABLE customers"
}
```

### Expected Response:
```json
{
  "success": true,
  "result": {
    "message": "Query executed successfully. Rows affected: 0"
  }
}
```

---

## 🎯 COMPLETE TEST SEQUENCE

### Quick Copy-Paste Sequence:

**1. Health Check**
```
GET http://localhost:8000/api/health
```

**2. List Tables (Before)**
```
POST http://localhost:8000/api/query/text
Content-Type: application/json

{
  "query": "List all tables in my database"
}
```

**3. Create Table**
```
POST http://localhost:8000/api/query/text
Content-Type: application/json

{
  "query": "Create a table called customers with id, name, and email"
}
```

**4. List Tables (After)**
```
POST http://localhost:8000/api/query/text
Content-Type: application/json

{
  "query": "List all tables in my database"
}
```

**5. Insert Data**
```
POST http://localhost:8000/api/query/text
Content-Type: application/json

{
  "query": "Insert into customers values (1, 'John Doe', 'john@example.com', GETDATE())"
}
```

**6. Query Data**
```
POST http://localhost:8000/api/query/text
Content-Type: application/json

{
  "query": "Select all from customers"
}
```

**7. Get Stats**
```
GET http://localhost:8000/api/stats
```

**8. Cleanup**
```
POST http://localhost:8000/api/query/text
Content-Type: application/json

{
  "query": "DROP TABLE customers"
}
```

---

## 📸 POSTMAN SCREENSHOTS GUIDE

### Request Setup:

```
┌─────────────────────────────────────────────────────────┐
│ POST ▼  http://localhost:8000/api/query/text    Send   │
├─────────────────────────────────────────────────────────┤
│ Params  Authorization  Headers  Body  Pre-request  Tests│
│                                                          │
│ Headers:                                                 │
│   Content-Type: application/json                        │
│                                                          │
│ Body: ○ none  ○ form-data  ○ x-www-form-urlencoded     │
│       ● raw   ○ binary     ○ GraphQL                    │
│                                                          │
│   JSON ▼                                                 │
│   ┌────────────────────────────────────────────────┐   │
│   │ {                                               │   │
│   │   "query": "List all tables in my database"    │   │
│   │ }                                               │   │
│   └────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

---

## 🔧 TROUBLESHOOTING

### Issue: Connection Refused
**Solution:** Make sure API is running
```bash
python run_api.py
```

### Issue: 404 Not Found
**Solution:** Check URL is correct
```
http://localhost:8000/api/query/text
```

### Issue: 500 Internal Server Error
**Solution:** Check API logs in terminal

### Issue: Invalid JSON
**Solution:** Make sure Body is set to **raw** and **JSON**

---

## 💾 SAVE AS POSTMAN COLLECTION

### Steps to Save:

1. Click **Save** button
2. Name: "SQL Server MCP API"
3. Create Collection: "Voice-Enabled SQL Server"
4. Save all requests

### Collection Structure:
```
Voice-Enabled SQL Server/
├── Health Check
├── List Tables
├── Create Table
├── Insert Data
├── Query Data
├── Get Statistics
└── Drop Table
```

---

## 🎓 FOR DEMO/PRESENTATION

### Demo Sequence:

1. **Show Health Check** - Prove API is running
2. **List Tables (Before)** - Show current state
3. **Create Table** - Show NL-to-SQL working
4. **List Tables (After)** - Prove table was created
5. **Insert Data** - Show data manipulation
6. **Query Data** - Show data retrieval
7. **Get Statistics** - Show RL learning
8. **Cleanup** - Drop table

### Key Points to Highlight:

- ✅ Natural language input
- ✅ Multiple SQL candidates generated
- ✅ RL agent selection
- ✅ Real database execution
- ✅ Performance metrics
- ✅ Caching working

---

## 📊 EXPECTED METRICS

After running all tests:

```json
{
  "cache": {
    "hit_rate": 0.14,  // 1 hit out of 7 queries
    "size": 6
  },
  "rl_agent": {
    "total_updates": 7,
    "epsilon": 0.093,  // Decaying
    "q_table_size": 4  // Learning states
  }
}
```

---

## ✅ VERIFICATION CHECKLIST

- [ ] API server running
- [ ] Health check returns 200
- [ ] Can list tables
- [ ] Can create table
- [ ] Table appears in list
- [ ] Can insert data
- [ ] Can query data
- [ ] Statistics show learning
- [ ] Can drop table

---

## 🎉 SUCCESS CRITERIA

**Your POC is working if:**
1. ✅ All requests return 200 OK
2. ✅ Table is created in database
3. ✅ Data can be inserted and queried
4. ✅ Statistics show RL learning
5. ✅ Cache hit rate increases

---

**💡 TIP:** Save all requests in a Postman Collection for easy re-testing!
