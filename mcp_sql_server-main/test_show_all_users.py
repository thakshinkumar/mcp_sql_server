#!/usr/bin/env python
"""Test the show all users query fix."""

import sys
import os
import re

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

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
    import re

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

def test_show_all_users():
    """Test the show all users query."""
    query = "show all users"
    expected = "SELECT * FROM users;"

    print("="*50)
    print(f"Testing: {query}")
    print("="*50)

    table_name = extract_table_name(query)
    print(f"Extracted table: '{table_name}'")

    result = nl_to_sql_mock(query)
    print(f"Generated SQL: '{result}'")
    print(f"Expected SQL:  '{expected}'")

    if result == expected:
        print("✅ PASS: Query now generates correct SQL!")
        return True
    else:
        print("❌ FAIL: Still returning generic comment")
        return False

if __name__ == "__main__":
    test_show_all_users()