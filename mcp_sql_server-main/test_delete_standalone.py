#!/usr/bin/env python
"""Standalone test of DELETE vs DROP logic."""

import re

def extract_table_name(query: str) -> str:
    """Extract table name from natural language query."""
    # Match patterns: "table users", "from users", "users table", "called users"
    # Avoid matching articles like "the"
    patterns = [
        r'(?:table|from|in)\s+(?!the\s|an?\s)(\w+)',  # Avoid "the" or "a/an" after from/in/table
        r'(?!the\s|an?\s)(\w+)\s+table',  # Avoid "the table" or "a table"
        r'called\s+(\w+)',
        r'to\s+(\w+)(?:\s|$)',
        r'(?:alter|drop|truncate|describe|create)\s+(?:table\s+)?(?!the\s|an?\s)(\w+)',  # Avoid articles
    ]

    query_lower = query.lower()
    for pattern in patterns:
        match = re.search(pattern, query_lower)
        if match:
            table_name = match.group(1)
            # Additional check: table name should not be an article
            if table_name not in ['the', 'a', 'an']:
                return table_name

    return None

def nl_to_sql_mock(query: str) -> str:
    """Mock NL-to-SQL conversion with DELETE vs DROP logic."""
    query_lower = query.lower()

    # ===== RULE 4: DROP TABLE vs DELETE FROM =====
    if ('drop' in query_lower or 'delete' in query_lower or 'remove' in query_lower):
        # Check for table operations (DROP TABLE or DELETE FROM)
        if 'table' in query_lower and 'column' not in query_lower and 'database' not in query_lower:
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

        # Check for data deletion operations (DELETE FROM without "table" keyword)
        elif 'delete' in query_lower and ('all' in query_lower or 'data' in query_lower or 'from' in query_lower or 'rows' in query_lower) and 'column' not in query_lower and 'database' not in query_lower:
            table_name = extract_table_name(query_lower)
            return f"DELETE FROM {table_name};"

    return None

def test_delete_logic():
    """Test the DELETE vs DROP logic directly."""
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
        ("delete all from employees", "DELETE FROM employees;"),
    ]

    print("="*60)
    print("STANDALONE TESTING: DELETE vs DROP LOGIC")
    print("="*60)

    all_passed = True

    for query, expected in test_cases:
        try:
            # Test table name extraction
            table_name = extract_table_name(query)
            print(f"\nQuery: '{query}'")
            print(f"Extracted table: '{table_name}'")

            # Test SQL generation
            generated_sql = nl_to_sql_mock(query)
            print(f"Generated SQL: '{generated_sql}'")
            print(f"Expected SQL:  '{expected}'")

            if generated_sql == expected:
                print("✓ PASS")
            else:
                print("✗ FAIL")
                all_passed = False

        except Exception as e:
            print(f"✗ ERROR: {e}")
            all_passed = False

    print("\n" + "="*60)
    if all_passed:
        print("✓ ALL TESTS PASSED!")
        print("\nSummary:")
        print("✓ 'delete the employees table' → DROP TABLE employees (removes table)")
        print("✓ 'delete all from employees' → DELETE FROM employees (removes rows)")
        print("✓ 'delete data from employees' → DELETE FROM employees (removes rows)")
        print("✓ 'delete rows from products' → DELETE FROM products (removes rows)")
    else:
        print("✗ SOME TESTS FAILED!")
    print("="*60)

    return all_passed

if __name__ == "__main__":
    test_delete_logic()