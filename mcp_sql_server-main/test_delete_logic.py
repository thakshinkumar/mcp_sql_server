#!/usr/bin/env python3
"""
Test the new DELETE vs DROP logic
"""

import re

def extract_table_name(query: str) -> str:
    """Extract table name from natural language query"""
    query_lower = query.lower()
    
    # Pattern 1: "table users" or "from users"
    match = re.search(r'(?:table|from|in)\s+(\w+)', query_lower)
    if match:
        return match.group(1)
    
    # Pattern 2: "users table"
    match = re.search(r'(\w+)\s+table', query_lower)
    if match:
        return match.group(1)
    
    # Pattern 3: "called users" or "named users"
    match = re.search(r'(?:called|named|as)\s+(\w+)', query_lower)
    if match:
        return match.group(1)
    
    return "new_table"

def test_delete_logic(query: str) -> str:
    """Test the DELETE vs DROP logic"""
    query_lower = query.lower()
    
    # ===== RULE 4: DROP TABLE vs DELETE FROM =====
    if ('drop' in query_lower or 'delete' in query_lower or 'remove' in query_lower) and 'table' in query_lower:
        # But exclude ALTER TABLE DROP COLUMN cases and DATABASE cases
        if 'column' not in query_lower and 'database' not in query_lower:
            table_name = extract_table_name(query_lower)
            
            # Distinguish between DROP TABLE and DELETE FROM
            # "delete the employees table" → DROP TABLE (remove table)
            # "delete all from employees" or "delete data from employees" → DELETE FROM (remove rows)
            if 'delete' in query_lower and ('all' in query_lower or 'data' in query_lower or 'from' in query_lower or 'rows' in query_lower):
                # DELETE FROM (remove all rows, keep table)
                return f"DELETE FROM {table_name};"
            else:
                # DROP TABLE (remove entire table)
                return f"DROP TABLE {table_name};"
    
    return "No match"

# Test cases
test_cases = [
    # DROP TABLE cases
    ("delete the employees table", "DROP TABLE employees;"),
    ("drop the users table", "DROP TABLE users;"),
    ("remove the products table", "DROP TABLE products;"),
    
    # DELETE FROM cases
    ("delete all data from employees", "DELETE FROM employees;"),
    ("delete all from users table", "DELETE FROM users;"),
    ("delete rows from products", "DELETE FROM products;"),
    ("delete data from the orders table", "DELETE FROM orders;"),
]

print("=" * 80)
print("TESTING DELETE vs DROP LOGIC")
print("=" * 80)
print()

all_passed = True
for query, expected in test_cases:
    result = test_delete_logic(query)
    passed = result == expected
    all_passed = all_passed and passed
    
    status = "✓" if passed else "✗"
    print(f"{status} Query:     {query}")
    print(f"  Expected:  {expected}")
    print(f"  Got:       {result}")
    if not passed:
        print(f"  ERROR: MISMATCH!")
    print()

print("=" * 80)
if all_passed:
    print("✓ ALL TESTS PASSED!")
    print()
    print("Summary:")
    print("✓ 'delete the employees table' → DROP TABLE employees (removes table)")
    print("✓ 'delete all from employees' → DELETE FROM employees (removes rows)")
    print("✓ 'delete data from employees' → DELETE FROM employees (removes rows)")
else:
    print("✗ SOME TESTS FAILED!")
print("=" * 80)
