# Voice-Enabled MCP-Based Self-Optimizing SQL Server - POC Setup Guide

## 🎯 Project Overview

This is a complete POC implementation of an intelligent SQL middleware system that:
- ✅ Accepts natural language queries (text input)
- ✅ Converts NL to SQL using LLM (with mock fallback)
- ✅ Generates multiple SQL candidates
- ✅ Selects optimal SQL using cost & latency evaluation
- ✅ Uses Q-Learning for adaptive optimization
- ✅ Caches query results
- ✅ Provides REST API interface
- ✅ Tracks metrics and learning progress
- 🔄 Voice input (placeholder for future implementation)

---

## 📋 Prerequisites

1. **Python 3.11+** installed
2. **SQL Server Express** installed and running
3. **TCP/IP enabled** on SQL Server (port 50998 or your configured port)
4. **Git** (if cloning from repository)

---

## 🚀 Quick Start (5 Minutes)

### Step 1: Install Dependencies

```bash
# Navigate to project directory
cd mssql_mcp_server-main

# Install required packages
pip install -r requirements.txt
```

### Step 2: Configure Environment

```bash
# Copy example environment file
copy .env.example .env

# Edit .env file with your SQL Server details
# For SQL Server Express with Windows Auth, use:
MSSQL_SERVER=localhost
MSSQL_PORT=50998
MSSQL_DATABASE=master
MSSQL_WINDOWS_AUTH=true
```

### Step 3: Test the POC

```bash
# Run the POC test script
python test_poc.py
```

You should see:
- ✅ Database connection successful
- ✅ Natural language queries converted to SQL
- ✅ Multiple SQL candidates generated
- ✅ Query execution with metrics
- ✅ Cache working (second query cached)
- ✅ RL agent learning and updating Q-values

---

## 🌐 Running the Web API

### Start the FastAPI Server

```bash
python run_api.py
```

The API will be available at:
- **API Root**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

### Test API Endpoints

#### 1. Health Check
```bash
curl http://localhost:8000/api/health
```

#### 2. Text Query
```bash
curl -X POST http://localhost:8000/api/query/text \
  -H "Content-Type: application/json" \
  -d "{\"query\": \"List all tables in my database\"}"
```

#### 3. Get Statistics
```bash
curl http://localhost:8000/api/stats
```

#### 4. Cache Statistics
```bash
curl http://localhost:8000/api/cache/stats
```

#### 5. RL Agent Statistics
```bash
curl http://localhost:8000/api/rl/stats
```

#### 6. Clear Cache
```bash
curl -X POST http://localhost:8000/api/cache/clear
```

---

## 📊 Testing Different Queries

### Example Natural Language Queries

```python
# In Python
import requests

queries = [
    "List all tables in my database",
    "Show me the SQL Server version",
    "Create a table called customers with id, name, and email",
    "Select all data from customers table",
]

for query in queries:
    response = requests.post(
        "http://localhost:8000/api/query/text",
        json={"query": query}
    )
    print(response.json())
```

### Using the Interactive Tester

```bash
python interactive_test.py
```

Then type natural language queries or SQL:
```
SQL> List all tables in my database
SQL> Show me the version
SQL> tables
SQL> exit
```

---

## 🧪 Understanding the System

### Architecture Flow

```
User Input (NL Query)
    ↓
[1] Check Cache → If HIT, return cached result
    ↓ (MISS)
[2] LLM Client → Generate 3 SQL candidates
    ↓
[3] RL Agent → Select best candidate (ε-greedy)
    ↓
[4] Cost Evaluator → Execute & measure performance
    ↓
[5] Calculate Reward → Update Q-table
    ↓
[6] Cache Result → Store for future queries
    ↓
Return Result to User
```

### Key Components

1. **LLM Client** (`nl_to_sql/llm_client.py`)
   - Converts NL to SQL
   - Generates multiple candidates
   - Uses mock mode if no API key provided

2. **Query Cache** (`cache/query_cache.py`)
   - LRU cache with TTL
   - Reduces redundant queries
   - Tracks hit/miss rates

3. **Cost Evaluator** (`optimizer/cost_evaluator.py`)
   - Measures execution time
   - Estimates query cost
   - Tracks success/failure

4. **Q-Learning Agent** (`rl/q_learning_agent.py`)
   - Learns optimal query selection
   - ε-greedy exploration/exploitation
   - Persists Q-table to database

5. **Orchestrator** (`orchestrator.py`)
   - Coordinates all components
   - Manages pipeline flow
   - Handles errors gracefully

---

## 📈 Monitoring & Metrics

### View System Statistics

```python
import requests

stats = requests.get("http://localhost:8000/api/stats").json()

print("Cache Hit Rate:", stats['stats']['cache']['hit_rate'])
print("RL Updates:", stats['stats']['rl_agent']['total_updates'])
print("Epsilon:", stats['stats']['rl_agent']['epsilon'])
```

### Database Tables Created

The system automatically creates these tables:
- `query_history` - All executed queries
- `query_candidates` - Generated SQL candidates
- `optimization_metrics` - Performance metrics
- `query_cache` - Cached results
- `rl_state` - RL training data
- `q_table` - Q-learning values

Query them to see learning progress:
```sql
SELECT TOP 10 * FROM query_history ORDER BY timestamp DESC;
SELECT TOP 10 * FROM q_table ORDER BY last_updated DESC;
```

---

## 🎓 Academic Project Features

### 1. Natural Language to SQL
- Pattern matching for common queries
- LLM integration ready (OpenAI/Azure)
- Multiple candidate generation

### 2. Multi-Candidate SQL Generation
- Generates 3 different SQL variants
- Uses different approaches (joins, subqueries, etc.)
- Validates syntax before execution

### 3. Cost & Latency Evaluation
- Measures execution time (ms)
- Estimates query cost
- Tracks logical/physical reads

### 4. Reinforcement Learning
- **State**: Query pattern features
- **Action**: Select SQL candidate (0, 1, 2)
- **Reward**: -1 * (normalized_latency + normalized_cost)
- **Algorithm**: Q-Learning with ε-greedy policy
- **Update Rule**: Q(s,a) ← Q(s,a) + α[r + γ·max Q(s',a') - Q(s,a)]

### 5. Query Caching
- LRU eviction policy
- Configurable TTL
- Hash-based lookup

### 6. Adaptive Optimization
- Learns from execution feedback
- Epsilon decay for exploration→exploitation
- Persists learning across sessions

---

## 🔧 Configuration Options

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `MSSQL_SERVER` | localhost | SQL Server address |
| `MSSQL_PORT` | 1433 | SQL Server port |
| `MSSQL_DATABASE` | master | Database name |
| `MSSQL_WINDOWS_AUTH` | false | Use Windows authentication |
| `LLM_API_KEY` | "" | OpenAI API key (optional) |
| `LLM_MODEL` | gpt-4 | LLM model to use |
| `CACHE_ENABLED` | true | Enable query caching |
| `CACHE_TTL` | 3600 | Cache TTL in seconds |
| `RL_ENABLED` | true | Enable RL optimization |
| `RL_LEARNING_RATE` | 0.1 | Q-learning alpha |
| `RL_EPSILON` | 0.1 | Exploration rate |
| `OPTIMIZER_NUM_CANDIDATES` | 3 | SQL candidates to generate |

---

## 🐛 Troubleshooting

### Issue: "Unable to connect to SQL Server"
**Solution**: 
1. Check SQL Server is running: `Get-Service MSSQL$SQLEXPRESS`
2. Verify TCP/IP is enabled in SQL Server Configuration Manager
3. Check port number: `Get-ItemProperty -Path 'HKLM:\SOFTWARE\Microsoft\Microsoft SQL Server\MSSQL*\MSSQLServer\SuperSocketNetLib\Tcp\IPAll'`
4. Update `.env` with correct port

### Issue: "No SQL candidates generated"
**Solution**: 
- System uses mock mode without LLM API key
- Check query patterns in `llm_client.py`
- Add OpenAI API key for real LLM generation

### Issue: "Table already exists" error
**Solution**: 
- Metrics tables already created (this is normal)
- System handles this gracefully

### Issue: API not starting
**Solution**:
```bash
# Check if port 8000 is in use
netstat -ano | findstr :8000

# Kill process if needed
taskkill /PID <process_id> /F

# Or use different port
uvicorn mssql_mcp_server.api.main:app --port 8001
```

---

## 📚 Next Steps

### For Production Deployment:
1. Add OpenAI API key for real NL-to-SQL
2. Implement Azure Speech Services for voice input
3. Add Redis for distributed caching
4. Set up monitoring (Prometheus/Grafana)
5. Add authentication & authorization
6. Deploy with Docker/Kubernetes

### For Academic Project:
1. Generate architecture diagrams
2. Document RL algorithm with math
3. Create performance benchmarks
4. Write test cases
5. Prepare demo video
6. Create presentation slides

---

## 📞 Support

For issues or questions:
1. Check logs in console output
2. Review `.env` configuration
3. Test database connection with `test_connection.py`
4. Check API docs at http://localhost:8000/docs

---

## ✅ POC Checklist

- [x] Database connection working
- [x] Natural language to SQL conversion
- [x] Multi-candidate SQL generation
- [x] Cost & latency evaluation
- [x] Q-Learning implementation
- [x] Query caching
- [x] REST API interface
- [x] Metrics tracking
- [x] Learning persistence
- [ ] Voice input (placeholder)
- [ ] Production LLM integration (optional)

---

**🎉 POC is ready for demonstration and academic evaluation!**
