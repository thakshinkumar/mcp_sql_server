#!/usr/bin/env python
"""Direct test of DELETE vs DROP logic without server."""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from mssql_mcp_server.api.main import nl_to_sql_mock, extract_table_name

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
    print("DIRECT TESTING: DELETE vs DROP LOGIC")
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