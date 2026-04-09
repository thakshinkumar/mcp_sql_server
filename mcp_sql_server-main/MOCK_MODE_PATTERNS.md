# Mock Mode SQL Pattern Support

When OpenAI is unavailable (no API key or no credits), the system falls back to pattern-based SQL generation.

## Supported Patterns (100% tested)

### DDL Operations

#### CREATE TABLE
```
"Create a table called Products"
"Create table Employee with empId and empName columns"
"Create a table named Orders with orderId and orderDate"
```
Generates: `CREATE TABLE TableName (columns...)`

#### ALTER TABLE - ADD COLUMN
```
"Add a column named Brand to the Apps table"
"Add email column to Users table"
"Add price to Products"
```
Generates: `ALTER TABLE TableName ADD ColumnName DataType`

#### ALTER TABLE - DROP COLUMN
```
"Remove the word column in Text table"
"Drop email column from Users"
"Delete price column in Products table"
```
Generates: `ALTER TABLE TableName DROP COLUMN ColumnName`

#### DROP TABLE
```
"Drop the Mobile table"
"Delete the Orders table"
"Remove Products table"
```
Generates: `DROP TABLE TableName`

### DML Operations

#### INSERT
```
"Insert some dummy data to Text table"
"Insert data into Products"
"Add records to Users table"
```
Generates: `INSERT INTO TableName (columns) VALUES (values)`

#### UPDATE
```
"Update Products set price to 100"
"Update Users set name to John"
```
Generates: `UPDATE TableName SET Column = Value WHERE ID = 1`

#### DELETE (rows)
```
"Delete records from Users where id is 5"
"Remove data from Products"
```
Generates: `DELETE FROM TableName WHERE ID = 1`

#### SELECT
```
"Show me all data from Customers"
"List all records from Inventory"
"Get all data from Products"
"Select everything from Orders"
```
Generates: `SELECT * FROM TableName`

### Metadata Queries

#### List Tables
```
"List all tables"
"Show all tables"
"What tables exist"
```
Generates: `SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES`

#### Show Schema
```
"Show schema of Customers table"
"Describe Products table"
"What columns are in Users"
```
Generates: `SELECT COLUMN_NAME, DATA_TYPE... FROM INFORMATION_SCHEMA.COLUMNS`

#### Server Version
```
"What is the SQL Server version"
"Show server version"
```
Generates: `SELECT @@VERSION`

## Data Type Inference

The system automatically infers column data types based on column names:

| Column Name Contains | Inferred Type |
|---------------------|---------------|
| id, ID | INT |
| email, Email | VARCHAR(100) |
| phone, mobile, number | VARCHAR(20) |
| address, Address | VARCHAR(255) |
| age, Age | INT |
| date, Date, time, Time | DATETIME |
| price, cost, amount, salary | DECIMAL(10,2) |
| quantity, stock, count | INT |
| name, brand, title | VARCHAR(100) |
| description, comment, note, category | VARCHAR(255) |

## Entity Extraction

The system extracts:
- **Table names** from patterns like "to the Apps table", "in Users", "from Products"
- **Column names** from patterns like "column named Brand", "add email", "remove word"
- Preserves original case from user input

## Pattern Priority

Patterns are checked in this order:
1. CREATE TABLE
2. List tables
3. Show schema (excluding ADD/DROP/ALTER)
4. Server version
5. Customer-specific queries (legacy)
6. DROP COLUMN (before DROP TABLE)
7. ALTER TABLE ADD COLUMN
8. DROP TABLE (excluding column operations)
9. INSERT
10. UPDATE
11. DELETE rows
12. Generic CREATE TABLE
13. Generic SELECT
14. Fallback (unsupported pattern message)

## Limitations

Mock mode is a fallback for when OpenAI is unavailable. For best results:
- Use OpenAI with GPT-4 (handles all queries accurately)
- Mock mode handles common patterns but may not understand complex queries
- Complex WHERE clauses, JOINs, subqueries require OpenAI

## Testing

Run comprehensive tests:
```bash
python test_entity_extraction.py
```

Current test results: 30/30 passed (100%)
