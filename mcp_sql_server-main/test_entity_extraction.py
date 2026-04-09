"""Test enhanced entity extraction in mock mode."""

import sys
sys.path.insert(0, 'src')

from mssql_mcp_server.nl_to_sql.llm_client import LLMClient
from mssql_mcp_server.config import config

def test_extraction(query, expected_table=None, expected_column=None):
    """Test entity extraction from natural language."""
    print(f"\n{'='*70}")
    print(f"Query: {query}")
    print(f"{'='*70}")
    
    client = LLMClient(config)
    sql_queries = client._mock_generate_sql(query)
    
    print(f"\nGenerated SQL:")
    for i, sql in enumerate(sql_queries, 1):
        print(f"  {i}. {sql}")
    
    # Check if expected entities are in the SQL
    if expected_table:
        found = any(expected_table in sql for sql in sql_queries)
        status = "[PASS]" if found else "[FAIL]"
        print(f"\n{status} Table '{expected_table}': {'Found' if found else 'NOT FOUND'}")
    
    if expected_column:
        found = any(expected_column in sql for sql in sql_queries)
        status = "[PASS]" if found else "[FAIL]"
        print(f"{status} Column '{expected_column}': {'Found' if found else 'NOT FOUND'}")
    
    return sql_queries

if __name__ == "__main__":
    print("Testing Enhanced Entity Extraction")
    print("="*70)
    
    tests = [
        # ALTER TABLE - ADD COLUMN tests (10 tests)
        ("Add a column named Brand to the Apps table", "Apps", "Brand"),
        ("Add email column to Users table", "Users", "email"),
        ("Add price to Products", "Products", "price"),
        ("Add address column in Customers table", "Customers", "address"),
        ("Add phone number to Employee", "Employee", "phone"),
        ("Add quantity column to Inventory table", "Inventory", "quantity"),
        ("Add description to Items", "Items", "description"),
        ("Add age column in Students table", "Students", "age"),
        ("Add salary to Staff table", "Staff", "salary"),
        ("Add category column to Books", "Books", "category"),
        
        # CREATE TABLE tests (10 tests)
        ("Create a table called Products with id and name", "Products", "id"),
        ("Create table Employee with empId and empName columns", "Employee", "empId"),
        ("Create a table named Orders with orderId and orderDate", "Orders", "orderId"),
        ("Create table Students with rollNo, name and branch", "Students", "rollNo"),
        ("Create a table called Inventory", "Inventory", None),
        ("Create table Books with bookId, title and author columns", "Books", "bookId"),
        ("Create a table named Customers with id and email", "Customers", "id"),
        ("Create table Suppliers with supplierId and supplierName", "Suppliers", "supplierId"),
        ("Create a table called Transactions with transactionId and amount", "Transactions", "transactionId"),
        ("Create table Categories with categoryId and categoryName columns", "Categories", "categoryId"),
        
        # DROP TABLE tests (5 tests)
        ("Drop the Mobile table", "Mobile", None),
        ("Delete the Orders table", "Orders", None),
        ("Remove Products table", "Products", None),
        ("Drop table Customers", "Customers", None),
        ("Delete the Inventory table", "Inventory", None),
        
        # SELECT tests (5 tests)
        ("Show me all data from Customers", "Customers", None),
        ("List all records from Inventory", "Inventory", None),
        ("Get all data from Products", "Products", None),
        ("Show all records in Orders", "Orders", None),
        ("List everything from Employees", "Employees", None),
    ]
    
    print(f"\nRunning {len(tests)} tests...\n")
    
    passed = 0
    failed = 0
    total = len(tests)
    failed_tests = []
    
    for query, expected_table, expected_column in tests:
        sql_queries = test_extraction(query, expected_table, expected_column)
        
        # Check if extraction was successful
        table_ok = not expected_table or any(expected_table in sql for sql in sql_queries)
        column_ok = not expected_column or any(expected_column in sql for sql in sql_queries)
        
        if table_ok and column_ok:
            passed += 1
        else:
            failed += 1
            failed_tests.append((query, expected_table, expected_column, sql_queries[0]))
    
    print("\n" + "="*70)
    print(f"RESULTS: {passed}/{total} tests passed ({failed} failed)")
    print("="*70)
    
    if failed_tests:
        print("\nFailed Tests:")
        print("-"*70)
        for query, exp_table, exp_col, generated_sql in failed_tests:
            print(f"\nQuery: {query}")
            print(f"Expected: Table='{exp_table}', Column='{exp_col}'")
            print(f"Generated: {generated_sql}")
    else:
        print("\n[SUCCESS] All tests passed!")
    
    # Calculate pass rate
    pass_rate = (passed / total) * 100
    print(f"\nPass Rate: {pass_rate:.1f}%")
    print("="*70)
