#!/usr/bin/env python
"""Direct test of the updated API functions."""

import sys
import os
import re

# Add src to path
sys.path.insert(0, 'src')

def extract_table_name(query: str) -> str:
    """Extract table name from natural language query."""
    patterns = [
        r'(?:table|from|in)\s+(?!the\s|an?\s)(\w+)',  # Avoid "the" or "a/an" after from/in/table
        r'(?!the\s|an?\s)(\w+)\s+table',  # Avoid "the table" or "a table"
        r'called\s+(\w+)',
        r'to\s+(\w+)(?:\s|$)',
        r'(?:alter|drop|truncate|describe|create)\s+(?:table\s+)?(?!the\s|an?\s)(\w+)',  # Avoid articles
        r'show\s+all\s+(?!the\s|an?\s)(\w+)',  # Match "show all users", "show all products", etc.
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

def nl_to_sql_mock(nl_query: str) -> str:
    """DDL-focused SQL generation with rule-based mapping."""
    query_lower = nl_query.lower()

    # ===== RULE 2: LIST ALL TABLES =====
    if any(phrase in query_lower for phrase in ['show all tables', 'list tables', 'database tables', 'list all tables']):
        return "SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE';"

    # ===== RULE 2.5: SHOW ALL DATA FROM TABLE =====
    if 'show all' in query_lower and 'table' not in query_lower and 'tables' not in query_lower:
        table_name = extract_table_name(query_lower)
        if table_name:
            return f"SELECT * FROM {table_name};"

    # Default: Return error message
    return "-- DDL-based NL2SQL: CREATE/DROP DATABASE, DESCRIBE TABLE, LIST TABLES, CREATE/DROP/ALTER TABLE, TRUNCATE, RENAME"

if __name__ == "__main__":
    # Test the fix
    test_cases = [
        ("show all users", "SELECT * FROM users;"),
        ("show all products", "SELECT * FROM products;"),
        ("show all tables", "SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE';"),
    ]

    print("Testing updated API functions:")
    print("=" * 50)

    for query, expected in test_cases:
        result = nl_to_sql_mock(query)
        status = "✅ PASS" if result == expected else "❌ FAIL"
        print(f"{query} -> {result} {status}")

    print("=" * 50)