# 🎮 COMMAND REFERENCE

## Quick Command Guide for POC

---

## 🚀 SETUP COMMANDS

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
# Copy example config
copy .env.example .env

# Edit .env with your settings
notepad .env
```

### 3. Verify Database Connection
```bash
python test_connection.py
```

---

## 🧪 TESTING COMMANDS

### Run Complete POC Test
```bash
python test_poc.py
```

**Expected Output:**
- ✅ Database connection
- ✅ 3 queries tested
- ✅ Cache hit demonstrated
- ✅ RL learning shown
- ✅ Statistics displayed

### Run Interactive Tester
```bash
python interactive_test.py
```

**Usage:**
```
SQL> List all tables in my database
SQL> Show me the version
SQL> tables
SQL> exit
```

---

## 🌐 API COMMANDS

### Start API Server
```bash
python run_api.py
```

**Access Points:**
- API Root: http://localhost:8000
- Interactive Docs: http://localhost:8000/docs
- Alternative Docs: http://localhost:8000/redoc

### Stop API Server
```
Press Ctrl+C in the terminal
```

---

## 📡 API ENDPOINT COMMANDS

### Health Check
```bash
curl http://localhost:8000/api/health
```

### Text Query
```bash
curl -X POST http://localhost:8000/api/query/text \
  -H "Content-Type: application/json" \
  -d "{\"query\": \"List all tables in my database\"}"
```

### Get System Statistics
```bash
curl http://localhost:8000/api/stats
```

### Get Cache Statistics
```bash
curl http://localhost:8000/api/cache/stats
```

### Get RL Agent Statistics
```bash
curl http://localhost:8000/api/rl/stats
```

### Clear Cache
```bash
curl -X POST http://localhost:8000/api/cache/clear
```

---

## 🐍 PYTHON API USAGE

### Simple Query
```python
import requests

response = requests.post(
    "http://localhost:8000/api/query/text",
    json={"query": "List all tables in my database"}
)

result = response.json()
print(f"Success: {result['success']}")
print(f"Selected SQL: {result['selected_sql']}")
print(f"Execution Time: {result['metrics']['execution_time_ms']}ms")
```

### Get Statistics
```python
import requests

stats = requests.get("http://localhost:8000/api/stats").json()

print("Cache Hit Rate:", stats['stats']['cache']['hit_rate'])
print("RL Updates:", stats['stats']['rl_agent']['total_updates'])
print("Epsilon:", stats['stats']['rl_agent']['epsilon'])
```

### Multiple Queries
```python
import requests

queries = [
    "List all tables in my database",
    "Show me the SQL Server version",
    "Create a table called customers",
]

for query in queries:
    response = requests.post(
        "http://localhost:8000/api/query/text",
        json={"query": query}
    )
    result = response.json()
    print(f"\nQuery: {query}")
    print(f"Success: {result['success']}")
    print(f"Cached: {result['cached']}")
```

---

## 🗄️ DATABASE COMMANDS

### View Query History
```sql
-- Connect to SQL Server and run:
SELECT TOP 10 * FROM query_history ORDER BY timestamp DESC;
```

### View Q-Table
```sql
SELECT TOP 10 * FROM q_table ORDER BY last_updated DESC;
```

### View Cache
```sql
SELECT TOP 10 * FROM query_cache ORDER BY created_at DESC;
```

### View Candidates
```sql
SELECT TOP 10 * FROM query_candidates ORDER BY timestamp DESC;
```

### Clear All Metrics (Reset)
```sql
TRUNCATE TABLE query_history;
TRUNCATE TABLE query_candidates;
TRUNCATE TABLE q_table;
TRUNCATE TABLE query_cache;
```

---

## 🔧 CONFIGURATION COMMANDS

### View Current Config
```bash
type .env
```

### Edit Config
```bash
notepad .env
```

### Reset to Default
```bash
copy .env.example .env
```

---

## 📊 MONITORING COMMANDS

### Watch API Logs (Real-time)
```bash
# Start API with verbose logging
python run_api.py
```

### Check SQL Server Status
```powershell
Get-Service MSSQL$SQLEXPRESS
```

### Check Port Usage
```powershell
netstat -ano | findstr :8000
netstat -ano | findstr :50998
```

---

## 🐛 TROUBLESHOOTING COMMANDS

### Test Database Connection
```bash
python test_connection.py
```

### Check Python Version
```bash
python --version
```

### List Installed Packages
```bash
pip list
```

### Reinstall Dependencies
```bash
pip install -r requirements.txt --force-reinstall
```

### Check SQL Server Port
```powershell
Get-ItemProperty -Path 'HKLM:\SOFTWARE\Microsoft\Microsoft SQL Server\MSSQL*\MSSQLServer\SuperSocketNetLib\Tcp\IPAll'
```

### Restart SQL Server
```powershell
# Run as Administrator
Restart-Service -Name 'MSSQL$SQLEXPRESS' -Force
```

---

## 📦 PACKAGE MANAGEMENT

### Install Single Package
```bash
pip install fastapi
pip install uvicorn
pip install python-dotenv
```

### Upgrade Package
```bash
pip install --upgrade fastapi
```

### Uninstall Package
```bash
pip uninstall fastapi
```

---

## 🎯 DEMO COMMANDS

### Full Demo Sequence
```bash
# 1. Start API
python run_api.py

# 2. In another terminal, run test
python test_poc.py

# 3. Test API endpoint
curl -X POST http://localhost:8000/api/query/text \
  -H "Content-Type: application/json" \
  -d "{\"query\": \"List all tables\"}"

# 4. Get statistics
curl http://localhost:8000/api/stats

# 5. Open browser
start http://localhost:8000/docs
```

---

## 🔄 RESET COMMANDS

### Reset Learning (Clear Q-Table)
```sql
TRUNCATE TABLE q_table;
```

### Reset Cache
```bash
curl -X POST http://localhost:8000/api/cache/clear
```

### Reset All Data
```sql
TRUNCATE TABLE query_history;
TRUNCATE TABLE query_candidates;
TRUNCATE TABLE optimization_metrics;
TRUNCATE TABLE query_cache;
TRUNCATE TABLE rl_state;
TRUNCATE TABLE q_table;
```

---

## 📝 LOGGING COMMANDS

### Enable Debug Logging
```bash
# Edit .env
LOG_LEVEL=DEBUG

# Restart API
python run_api.py
```

### View Logs
```bash
# Logs are printed to console
# Redirect to file:
python run_api.py > api.log 2>&1
```

---

## 🚀 PRODUCTION COMMANDS (Future)

### Run with Gunicorn
```bash
gunicorn -w 4 -k uvicorn.workers.UvicornWorker mssql_mcp_server.api.main:app
```

### Run with Docker
```bash
docker build -t mssql-mcp-server .
docker run -p 8000:8000 --env-file .env mssql-mcp-server
```

### Run with Docker Compose
```bash
docker-compose up -d
docker-compose logs -f
docker-compose down
```

---

## 📚 DOCUMENTATION COMMANDS

### View API Docs
```bash
start http://localhost:8000/docs
```

### Generate OpenAPI Spec
```bash
curl http://localhost:8000/openapi.json > openapi.json
```

---

## ✅ QUICK REFERENCE

| Task | Command |
|------|---------|
| Test POC | `python test_poc.py` |
| Start API | `python run_api.py` |
| Interactive Test | `python interactive_test.py` |
| Health Check | `curl http://localhost:8000/api/health` |
| Query API | `curl -X POST http://localhost:8000/api/query/text -H "Content-Type: application/json" -d "{\"query\": \"...\"}"` |
| Get Stats | `curl http://localhost:8000/api/stats` |
| Clear Cache | `curl -X POST http://localhost:8000/api/cache/clear` |
| View Docs | `start http://localhost:8000/docs` |

---

**💡 Tip**: Keep the API running in one terminal and test in another!
