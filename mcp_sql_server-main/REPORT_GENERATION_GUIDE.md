# Report Generation Guide

This guide explains how to generate comprehensive report materials for your project demonstration.

## Prerequisites

Make sure you have these packages installed:
```bash
pip install matplotlib pandas requests
```

## Available Tools

### 1. 📊 Comprehensive Report Generator (`generate_report_data.py`)

Generates all report materials in one go:
- Latency performance graphs (PNG)
- Query proof document (HTML)
- Screenshot-ready demo output (TXT)
- RL learning comparison charts (PNG)
- Raw performance data (CSV)

**Usage:**
```bash
# Make sure API server is running
python run_api.py

# In another terminal
python generate_report_data.py
```

**Output Files:**
- `latency_graph_YYYYMMDD_HHMMSS.png` - Performance visualization
- `latency_data_YYYYMMDD_HHMMSS.csv` - Raw data for analysis
- `query_proof_YYYYMMDD_HHMMSS.html` - Open in browser for proof
- `demo_output_YYYYMMDD_HHMMSS.txt` - Text output for screenshots
- `rl_comparison_YYYYMMDD_HHMMSS.png` - RL learning visualization

### 2. 📸 Quick Demo Script (`quick_demo.py`)

Interactive demo for live screenshots:
- Step-by-step query execution
- Formatted console output
- Pause between queries for screenshots

**Usage:**
```bash
python quick_demo.py
```

**Features:**
- 8 different query types demonstrated
- Press Enter to advance between queries
- Perfect for capturing screenshots
- Shows all query details (NL, SQL, metrics, results)

### 3. 📝 Project Report Template (`PROJECT_REPORT_TEMPLATE.md`)

Complete report structure with sections for:
- Executive summary
- System architecture
- Implementation details
- Performance results
- Query examples
- API documentation
- Testing & validation
- Screenshots placeholders
- Future enhancements

**Usage:**
1. Open `PROJECT_REPORT_TEMPLATE.md`
2. Fill in your specific details
3. Insert generated screenshots
4. Export to PDF or submit as-is

## Step-by-Step Report Creation

### Step 1: Generate All Data
```bash
# Terminal 1: Start API server
python run_api.py

# Terminal 2: Generate report data
python generate_report_data.py
```

This creates:
- ✅ Performance graphs
- ✅ Proof document
- ✅ Demo output
- ✅ RL comparison

### Step 2: Capture Screenshots

#### Option A: Use Quick Demo (Recommended)
```bash
python quick_demo.py
```
- Take screenshots at each step
- Shows formatted output perfect for reports

#### Option B: Use Postman
1. Open Postman
2. Import collection from `POSTMAN_GUIDE.md`
3. Execute queries
4. Screenshot the responses

#### Option C: Use Browser
1. Open `query_proof_YYYYMMDD_HHMMSS.html` in browser
2. Take full-page screenshot
3. Use for "Query Proof" section

### Step 3: Organize Screenshots

Create a folder structure:
```
screenshots/
├── 1_system_architecture.png
├── 2_latency_graph.png
├── 3_query_proof.png
├── 4_demo_output.png
├── 5_rl_comparison.png
└── 6_api_response.png
```

### Step 4: Complete Report

1. Open `PROJECT_REPORT_TEMPLATE.md`
2. Fill in your details:
   - Your name
   - Project dates
   - Specific metrics from generated data
3. Insert screenshots in marked sections
4. Add any additional observations

### Step 5: Export to PDF (Optional)

**Using Markdown to PDF tools:**
```bash
# Using pandoc (if installed)
pandoc PROJECT_REPORT_TEMPLATE.md -o project_report.pdf

# Or use online converters:
# - https://www.markdowntopdf.com/
# - https://dillinger.io/
```

## Screenshot Tips

### For Console Output
1. Use a terminal with good contrast (dark theme recommended)
2. Increase font size for readability
3. Capture full output including headers
4. Use `quick_demo.py` for best formatting

### For Graphs
1. Generated graphs are already high-resolution (300 DPI)
2. No need to screenshot - use PNG files directly
3. Graphs include:
   - Latency comparison
   - RL learning curves
   - Query type distribution

### For HTML Proof
1. Open in Chrome/Firefox
2. Use full-page screenshot extension
3. Or use browser's built-in PDF export
4. Ensure all query blocks are visible

### For API Responses
1. Use Postman's "Visualize" tab
2. Or format JSON in browser with extension
3. Highlight important fields (success, metrics, result)

## What to Include in Report

### Must-Have Screenshots
1. ✅ Latency graph showing performance
2. ✅ Query proof document (HTML)
3. ✅ Live demo output (console)
4. ✅ RL learning comparison
5. ✅ API response example

### Optional Screenshots
- System architecture diagram
- Database schema
- Test results
- Error handling examples
- Configuration files

## Example Report Structure

```
1. Cover Page
   - Project title
   - Your name
   - Date

2. Table of Contents

3. Introduction
   - Screenshot: System architecture

4. Implementation
   - Screenshot: Code structure

5. Performance Results
   - Screenshot: Latency graph
   - Screenshot: RL comparison

6. Query Examples
   - Screenshot: Query proof HTML
   - Screenshot: Demo output

7. API Documentation
   - Screenshot: Postman response

8. Testing
   - Screenshot: Test results

9. Conclusion

10. Appendices
```

## Troubleshooting

### Issue: API Connection Error
**Solution:** Make sure `python run_api.py` is running

### Issue: Matplotlib Not Found
**Solution:** `pip install matplotlib pandas`

### Issue: No Data in Graphs
**Solution:** Execute some queries first to generate data

### Issue: HTML Not Opening
**Solution:** Right-click file → Open with → Browser

## Quick Checklist

Before submitting your report:
- [ ] All graphs generated
- [ ] Query proof HTML created
- [ ] Demo output captured
- [ ] Screenshots organized
- [ ] Report template filled
- [ ] Metrics verified
- [ ] All sections complete
- [ ] PDF exported (if required)

## Additional Resources

- `MOCK_MODE_PATTERNS.md` - Pattern matching documentation
- `ENTITY_EXTRACTION_GUIDE.md` - NL processing details
- `POSTMAN_GUIDE.md` - API testing guide
- `QUICK_START.md` - Setup instructions

## Support

If you need help:
1. Check error messages in console
2. Verify API server is running
3. Check database connection
4. Review generated log files

---

**Good luck with your project report! 🚀**
