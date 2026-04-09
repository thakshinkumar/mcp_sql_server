# Enhanced Entity Extraction Guide

## What Changed

The mock SQL generator now has much better entity extraction that can identify:
- Table names from natural language
- Column names from natural language
- Appropriate data types based on column names

## Supported Patterns

### CREATE TABLE
```
"Create a table called Products"
"Create table Employee with id and name"
"Make a table named Orders"
```
Extracts: Table name (Products, Employee, Orders)

### ALTER TABLE - ADD COLUMN
```
"Add a column named Brand to the Apps table"
"Add email to Users table"
"Add price column in Products"
```
Extracts: 
- Table name (Apps, Users, Products)
- Column name (Brand, email, price)
- Infers data type from column name

### DROP TABLE
```
"Drop the Mobile table"
"Delete the Orders table"
"Remove Products table"
```
Extracts: Table name (Mobile, Orders, Products)

### SELECT
```
"Show me all data from Customers"
"List all records from Inventory"
"Get data from Apps"
```
Extracts: Table name (Customers, Inventory, Apps)

## Column Type Inference

The system automatically infers data types based on column names:

| Column Name Contains | Data Type |
|---------------------|-----------|
| id, ID | INT |
| email, Email | VARCHAR(100) |
| phone, mobile, Mobile | VARCHAR(20) |
| address, Address | VARCHAR(255) |
| age, Age | INT |
| date, Date, time, Time | DATETIME |
| price, Price, cost, amount | DECIMAL(10,2) |
| quantity, stock, count | INT |
| name, Name, brand, Brand, title | VARCHAR(100) |
| description, comment, note | VARCHAR(255) |

## Testing

Test the entity extraction:
```bash
python test_entity_extraction.py
```

Test with the API:
```bash
# Make sure server is running
python run_api.py

# In another terminal, test
curl -X POST http://localhost:8000/api/query/text \
  -H "Content-Type: application/json" \
  -d '{"query": "Add a column named Brand to the Apps table"}'
```

## Examples

### Before Enhancement
```
Query: "Add a column named Brand to the Apps table"
SQL: ALTER TABLE Customers ADD NewColumn VARCHAR(100)
❌ Wrong table, wrong column
```

### After Enhancement
```
Query: "Add a column named Brand to the Apps table"
SQL: ALTER TABLE Apps ADD Brand VARCHAR(100)
✅ Correct table, correct column
```

## Limitations

This is still mock mode with pattern matching. For production:
- Use OpenAI with sufficient credits
- Or integrate a local model like Ollama with SQLCoder
- Mock mode is for testing/demo only

## Next Steps

1. Restart the server: `python run_api.py`
2. Test with your queries
3. If you need better accuracy, add OpenAI credits or set up Ollama
