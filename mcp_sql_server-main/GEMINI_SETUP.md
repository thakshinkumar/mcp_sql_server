# 🤖 GEMINI API SETUP GUIDE

## How to Use Google Gemini for Real NL-to-SQL

---

## 🎯 WHY USE GEMINI?

- ✅ **Free tier available** - No credit card required
- ✅ **Fast responses** - Low latency
- ✅ **Good at SQL** - Trained on code
- ✅ **Easy setup** - Simple API key
- ✅ **Alternative to OpenAI** - No OpenAI account needed

---

## 📝 STEP 1: GET GEMINI API KEY

### 1. Go to Google AI Studio
Visit: https://makersuite.google.com/app/apikey

### 2. Sign in with Google Account
Use any Google account (Gmail, etc.)

### 3. Create API Key
- Click **"Get API Key"** or **"Create API Key"**
- Select **"Create API key in new project"**
- Copy the API key (starts with `AIza...`)

### 4. Save Your API Key
⚠️ **IMPORTANT**: Save it somewhere safe! You won't be able to see it again.

---

## 🔧 STEP 2: CONFIGURE THE SYSTEM

### Option A: Edit .env File

Open `.env` file and update:

```bash
# LLM Configuration
LLM_PROVIDER=gemini
LLM_API_KEY=AIzaSyD...your_actual_key_here...
LLM_MODEL=gemini-pro
LLM_TEMPERATURE=0.3
LLM_MAX_TOKENS=500
```

### Option B: Set Environment Variable

```bash
# Windows CMD
set LLM_PROVIDER=gemini
set LLM_API_KEY=AIzaSyD...your_actual_key_here...
set LLM_MODEL=gemini-pro

# Windows PowerShell
$env:LLM_PROVIDER="gemini"
$env:LLM_API_KEY="AIzaSyD...your_actual_key_here..."
$env:LLM_MODEL="gemini-pro"
```

---

## 📦 STEP 3: INSTALL GEMINI LIBRARY

```bash
pip install google-generativeai
```

---

## ✅ STEP 4: TEST IT

### Test 1: Quick Test Script

```bash
python -c "import google.generativeai as genai; genai.configure(api_key='YOUR_API_KEY'); model = genai.GenerativeModel('gemini-pro'); response = model.generate_content('Say hello'); print(response.text)"
```

Replace `YOUR_API_KEY` with your actual key.

### Test 2: Run POC Test

```bash
python test_poc.py
```

You should see:
```
✓ Gemini client initialized successfully
```

Instead of:
```
⚠ No LLM API key provided. Using mock mode.
```

### Test 3: Try a Real Query

```bash
python run_api.py
```

Then:
```bash
curl -X POST http://localhost:8000/api/query/text \
  -H "Content-Type: application/json" \
  -d "{\"query\": \"Create a table for storing employee information with id, name, department, and salary\"}"
```

---

## 🎯 WHAT CHANGES WITH GEMINI?

### Before (Mock Mode):
- Uses pattern matching
- Limited query types
- Predefined SQL templates

### After (Gemini Mode):
- Real AI understanding
- Handles complex queries
- Generates optimized SQL
- Better natural language understanding

---

## 📊 EXAMPLE QUERIES WITH GEMINI

### Simple Queries:
```
"Show me all customers"
"List products with price greater than 100"
"Count how many orders we have"
```

### Complex Queries:
```
"Show me the top 5 customers by total order value"
"Find all products that haven't been ordered in the last 30 days"
"Calculate the average salary by department"
```

### Schema Queries:
```
"Create a table for tracking inventory with product id, quantity, and last updated date"
"Add a foreign key relationship between orders and customers"
"Create an index on the email column of the users table"
```

---

## 🔍 VERIFY GEMINI IS WORKING

### Check Logs:

When you run the system, you should see:
```
INFO - Gemini client initialized successfully
```

### Check API Response:

The generated SQL should be more sophisticated:
```json
{
  "candidates": [
    "SELECT TOP 5 c.customer_id, c.name, SUM(o.total) as total_value FROM customers c JOIN orders o ON c.id = o.customer_id GROUP BY c.customer_id, c.name ORDER BY total_value DESC",
    "WITH customer_totals AS (SELECT customer_id, SUM(total) as total FROM orders GROUP BY customer_id) SELECT TOP 5 c.*, ct.total FROM customers c JOIN customer_totals ct ON c.id = ct.customer_id ORDER BY ct.total DESC",
    "SELECT TOP 5 * FROM (SELECT c.*, SUM(o.total) OVER (PARTITION BY c.id) as total_value FROM customers c LEFT JOIN orders o ON c.id = o.customer_id) sub ORDER BY total_value DESC"
  ]
}
```

---

## 💰 GEMINI PRICING

### Free Tier:
- **60 requests per minute**
- **1,500 requests per day**
- **1 million tokens per month**

This is **MORE than enough** for POC and academic projects!

### Rate Limits:
If you hit rate limits, the system will:
1. Log a warning
2. Fall back to mock mode
3. Continue working

---

## 🔧 TROUBLESHOOTING

### Issue: "Module 'google.generativeai' not found"

**Solution:**
```bash
pip install google-generativeai
```

### Issue: "API key not valid"

**Solution:**
1. Check your API key is correct
2. Make sure there are no extra spaces
3. Verify the key starts with `AIza`
4. Try generating a new key

### Issue: "Quota exceeded"

**Solution:**
1. Wait a minute (60 requests/minute limit)
2. System will fall back to mock mode automatically
3. Consider upgrading to paid tier if needed

### Issue: "Still using mock mode"

**Solution:**
1. Check `.env` file has correct API key
2. Restart the API server: `python run_api.py`
3. Check logs for error messages

---

## 🎓 FOR ACADEMIC PROJECT

### With Gemini API:

**Advantages:**
- ✅ Real AI-powered NL-to-SQL
- ✅ Better demo quality
- ✅ More impressive results
- ✅ Handles complex queries

**For Report:**
- Mention using Google Gemini Pro
- Show comparison: Mock vs Real AI
- Demonstrate complex query handling
- Include API integration details

### Without Gemini API (Mock Mode):

**Still Works:**
- ✅ All other features work
- ✅ RL learning works
- ✅ Caching works
- ✅ Cost evaluation works
- ✅ Pattern matching for common queries

**For Report:**
- Mention "Proof of Concept with mock NL-to-SQL"
- Focus on RL and optimization features
- Explain LLM integration is ready for production

---

## 📝 CONFIGURATION COMPARISON

### Mock Mode (.env):
```bash
LLM_PROVIDER=gemini
LLM_API_KEY=
LLM_MODEL=gemini-pro
```

### Gemini Mode (.env):
```bash
LLM_PROVIDER=gemini
LLM_API_KEY=AIzaSyD...your_key...
LLM_MODEL=gemini-pro
```

---

## 🚀 QUICK START WITH GEMINI

```bash
# 1. Get API key from https://makersuite.google.com/app/apikey

# 2. Install library
pip install google-generativeai

# 3. Update .env
notepad .env
# Add your API key to LLM_API_KEY=

# 4. Test it
python test_poc.py

# 5. Start API
python run_api.py

# 6. Try a complex query
curl -X POST http://localhost:8000/api/query/text \
  -H "Content-Type: application/json" \
  -d "{\"query\": \"Show me the top 10 most expensive products\"}"
```

---

## 📊 GEMINI MODELS AVAILABLE

| Model | Description | Best For |
|-------|-------------|----------|
| `gemini-pro` | Standard model | General SQL generation |
| `gemini-pro-vision` | With image support | Not needed for SQL |
| `gemini-1.5-pro` | Latest version | Better accuracy |

**Recommended**: Use `gemini-pro` for this project.

---

## ✅ CHECKLIST

- [ ] Got Gemini API key from Google AI Studio
- [ ] Installed `google-generativeai` library
- [ ] Updated `.env` with API key
- [ ] Set `LLM_PROVIDER=gemini`
- [ ] Set `LLM_MODEL=gemini-pro`
- [ ] Tested with `python test_poc.py`
- [ ] Verified "Gemini client initialized" in logs
- [ ] Tested complex queries

---

## 🎉 BENEFITS OF USING GEMINI

1. **Free for POC** - No cost for academic projects
2. **Easy Setup** - Just one API key
3. **Good Performance** - Fast and accurate
4. **No Credit Card** - Unlike OpenAI
5. **Google Quality** - Reliable service

---

**💡 TIP**: Even without Gemini API, your POC works perfectly! The RL, caching, and optimization features are independent of the LLM provider.

**🎓 FOR VIVA**: You can demonstrate both modes - mock mode for reliability and Gemini mode for advanced featur