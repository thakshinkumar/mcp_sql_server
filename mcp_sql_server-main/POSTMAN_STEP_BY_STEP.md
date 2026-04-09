# 📮 POSTMAN STEP-BY-STEP VISUAL GUIDE

## Complete Visual Walkthrough for Testing

---

## 🎯 OBJECTIVE

Test the complete flow:
1. List tables (before)
2. Create new table
3. List tables (after) - verify table created
4. Insert data
5. Query data
6. View statistics

---

## 📋 PREREQUISITES

✅ API server running: `python run_api.py`  
✅ Postman installed and open  
✅ Database connected (localhost:50998/master)

---

## 🔷 TEST 1: LIST TABLES (BEFORE)

### Visual Setup:

```
┌─────────────────────────────────────────────────────────────┐
│ Postman Window                                              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  [POST ▼] [http://localhost:8000/api/query/text    ] [Send]│
│                                                             │
│  Tabs: Params | Authorization | Headers | Body | ...       │
│                                                             │
│  ┌─ Headers Tab ─────────────────────────────────────────┐ │
│  │ KEY              VALUE                                 │ │
│  │ Content-Type     application/json                     │ │
│  └───────────────────────────────────────────────────────┘ │
│                                                             │
│  ┌─ Body Tab ────────────────────────────────────────────┐ │
│  │ ○ none  ○ form-data  ○ x-www-form-urlencoded         │ │
│  │ ● raw   ○ binary     ○ GraphQL                        │ │
│  │                                                        │ │
│  │ [Text ▼] → Change to [JSON ▼]                         │ │
│  │                                                        │ │
│  │ {                                                      │ │
│  │   "query": "List all tables in my database"          │ │
│  │ }                                                      │ │
│  └───────────────────────────────────────────────────────┘ │
│                                                             │
│  [Send] ← Click this button                                │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Step-by-Step:

1. **Select Method:**
   - Click dropdown next to URL bar
   - Select `POST`

2. **Enter URL:**
   ```
   http://localhost:8000/api/query/text
   ```

3. **Add Header:**
   - Click `Headers` tab
   - Click in KEY field, type: `Content-Type`
   - Click in VALUE field, type: `application/json`

4. **Set Body:**
   - Click `Body` tab
   - Select `raw` radio button
   - Change dropdown from `Text` to `JSON`
   - Paste:
   ```json
   {
     "query": "List all tables in my database"
   }
   ```

5. **Send Request:**
   - Click blue `Send` button

### Expected Response:

```json
{
  "success": true,
  "input": "List all tables in my database",
  "candidates": [
    "SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE';",
    "SELECT name FROM sys.tables WHERE type = 'U';",
    "SELECT TABLE_SCHEMA + '.' + TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'"
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
    "estimated_cost": 0,
    "rows_affected": 5,
    "success": true,
    "error": null
  },
  "cached": false,
  "error": null
}
```

### What to Check:
- ✅ Status: `200 OK` (green)
- ✅ `success: true`
- ✅ 5 tables in `rows` array
- ✅ No `customers` table yet

---

## 🔷 TEST 2: CREATE TABLE

### Keep same setup, just change Body:

```json
{
  "query": "Create a table called customers with id as integer primary key, name as varchar 100, and email as varchar 100"
}
```

### Alternative (Direct SQL):

```json
{
  "query": "CREATE TABLE customers (id INT PRIMARY KEY, name VARCHAR(100), email VARCHAR(100))"
}
```

### Click Send

### Expected Response:

```json
{
  "success": true,
  "input": "Create a table called customers...",
  "candidates": [
    "CREATE TABLE customers (id INT PRIMARY KEY, name VARCHAR(100), email VARCHAR(100))",
    "CREATE TABLE dbo.customers (id INT IDENTITY(1,1) PRIMARY KEY, name NVARCHAR(100), email NVARCHAR(100))",
    "CREATE TABLE customers (id INTEGER NOT NULL PRIMARY KEY, name VARCHAR(100), email VARCHAR(100))"
  ],
  "selected_sql": "CREATE TABLE customers (id INT PRIMARY KEY, name VARCHAR(100), email VARCHAR(100))",
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

### What to Check:
- ✅ Status: `200 OK`
- ✅ `success: true`
- ✅ Message: "Query executed successfully"
- ✅ 3 SQL candidates generated
- ✅ RL agent selected one

---

## 🔷 TEST 3: LIST TABLES (AFTER)

### Change Body back to:

```json
{
  "query": "List all tables in my database"
}
```

### Click Send

### Expected Response:

```json
{
  "success": true,
  "result": {
    "columns": ["TABLE_NAME"],
    "rows": [
      ["customers"],              ← ✅ NEW TABLE HERE!
      ["MSreplication_options"],
      ["spt_fallback_db"],
      ["spt_fallback_dev"],
      ["spt_fallback_usg"],
      ["spt_monitor"]
    ]
  },
  "cached": false
}
```

### What to Check:
- ✅ Status: `200 OK`
- ✅ `customers` appears in rows
- ✅ Now 6 tables total (was 5 before)

---

## 🔷 TEST 4: INSERT DATA

### Change Body to:

```json
{
  "query": "Insert into customers values (1, 'John Doe', 'john@example.com')"
}
```

### Click Send

### Expected Response:

```json
{
  "success": true,
  "result": {
    "message": "Query executed successfully. Rows affected: 1"
  },
  "metrics": {
    "execution_time_ms": 45.67,
    "rows_affected": 1,
    "success": true
  }
}
```

### What to Check:
- ✅ Status: `200 OK`
- ✅ Rows affected: 1
- ✅ Success: true

---

## 🔷 TEST 5: QUERY DATA

### Change Body to:

```json
{
  "query": "Select all from customers"
}
```

### Click Send

### Expected Response:

```json
{
  "success": true,
  "result": {
    "columns": ["id", "name", "email"],
    "rows": [
      [1, "John Doe", "john@example.com"]
    ]
  },
  "metrics": {
    "execution_time_ms": 23.45,
    "rows_affected": 1,
    "success": true
  },
  "cached": false
}
```

### What to Check:
- ✅ Status: `200 OK`
- ✅ Data returned: John Doe
- ✅ All columns present

---

## 🔷 TEST 6: GET STATISTICS

### Change to GET request:

1. **Change Method:** `GET`
2. **Change URL:** `http://localhost:8000/api/stats`
3. **Remove Body** (not needed for GET)
4. **Click Send**

### Expected Response:

```json
{
  "success": true,
  "stats": {
    "cache": {
      "hits": 1,
      "misses": 5,
      "hit_rate": 0.1667,
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

### What to Check:
- ✅ Cache working (some hits)
- ✅ RL agent learning (updates > 0)
- ✅ Epsilon decaying (< 0.1)
- ✅ Q-table growing

---

## 🔷 VERIFICATION IN DATABASE

### Open another terminal:

```bash
python check_database.py
```

### You should see:

```
📊 USER TABLES:
------------------------------------------------------------

   📋 dbo.customers
      Rows: 1
      Columns: id, name, email
      Sample data:
        (1, 'John Doe', 'john@example.com')

   📋 dbo.MSreplication_options
      Rows: 3
      ...
```

**✅ Confirms table was created in real database!**

---

## 🔷 TEST 7: CLEANUP (OPTIONAL)

### Change back to POST:

1. **Method:** `POST`
2. **URL:** `http://localhost:8000/api/query/text`
3. **Body:**

```json
{
  "query": "DROP TABLE customers"
}
```

### Click Send

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

## 📊 COMPLETE FLOW SUMMARY

```
1. List Tables (Before)  → 5 tables
2. Create Table          → customers created
3. List Tables (After)   → 6 tables (customers added)
4. Insert Data           → 1 row inserted
5. Query Data            → John Doe returned
6. Get Statistics        → RL learning shown
7. Verify in DB          → Table exists in SQL Server
8. Cleanup               → Table dropped
```

---

## 🎯 SUCCESS INDICATORS

### All Tests Pass If:

- ✅ All responses return `200 OK`
- ✅ `success: true` in all responses
- ✅ Table appears in list after creation
- ✅ Data can be inserted and retrieved
- ✅ Statistics show learning progress
- ✅ `check_database.py` shows the table

---

## 💾 SAVE AS COLLECTION

### Create Collection:

1. Click `Collections` in left sidebar
2. Click `+` or `New Collection`
3. Name: "Voice-Enabled SQL Server POC"
4. Save each request:
   - Click `Save` after each request
   - Add to collection
   - Name appropriately

### Collection Structure:

```
Voice-Enabled SQL Server POC/
├── 1. Health Check
├── 2. List Tables (Before)
├── 3. Create Table
├── 4. List Tables (After)
├── 5. Insert Data
├── 6. Query Data
├── 7. Get Statistics
└── 8. Drop Table
```

---

## 🎓 FOR DEMO/VIVA

### Demo Script:

1. **Show API Running** - Terminal with `python run_api.py`
2. **Health Check** - Prove system is up
3. **List Tables** - Show current state
4. **Create Table** - Demonstrate NL-to-SQL
5. **Verify Creation** - Show table in list
6. **Insert & Query** - Show data operations
7. **Show Statistics** - Highlight RL learning
8. **Show Database** - Run `check_database.py`

### Key Points to Mention:

- 🤖 **Gemini AI** generating SQL
- 🎯 **Multiple candidates** (3 variants)
- 🧠 **RL agent** selecting optimal query
- ⚡ **Real-time execution** on actual database
- 📊 **Performance tracking** and learning
- 💾 **Query caching** for efficiency

---

## 🐛 COMMON ISSUES

### Issue: "Connection refused"
**Fix:** Start API server
```bash
python run_api.py
```

### Issue: "Invalid JSON"
**Fix:** 
- Make sure Body is set to `raw`
- Dropdown is set to `JSON`
- JSON is valid (use JSON validator)

### Issue: "Table already exists"
**Fix:** Drop table first
```json
{"query": "DROP TABLE customers"}
```

### Issue: "Gemini quota exceeded"
**Fix:** Wait 15 seconds or system uses mock mode automatically

---

## ✅ FINAL CHECKLIST

- [ ] API server running
- [ ] Postman open
- [ ] Health check passes
- [ ] Can list tables
- [ ] Can create table
- [ ] Table appears in list
- [ ] Can insert data
- [ ] Can query data
- [ ] Statistics show learning
- [ ] Verified in database
- [ ] Collection saved

---

**🎉 You're ready to demonstrate your POC!**
