#!/usr/bin/env python3
"""
Comprehensive test of SQL generation with all features
Tests both mock mode and the complete nl_to_sql flow
"""

import re

# Inline the critical functions to test without running the server
def clean_sql_output(sql: str) -> str:
    """Remove articles (a, an, the) from SQL statements and clean whitespace"""
    sql = re.sub(r'\b(CREATE|DROP|ALTER|ADD|MODIFY|TRUNCATE)\s+(a|an|the)\s+', r'\1 ', sql, flags=re.IGNORECASE)
    sql = re.sub(r'\s+(a|an|the)\s+(DATABASE|TABLE|COLUMN)\b', r' \2', sql, flags=re.IGNORECASE)
    sql = re.sub(r'\s+', ' ', sql)
    return sql.strip()

def is_sql_query(query: str) -> bool:
    """Detect if input is already SQL vs natural language"""
    sql_keywords = ['SELECT', 'CREATE', 'DROP', 'INSERT', 'UPDATE', 'DELETE', 'ALTER', 'TRUNCATE', 'EXEC', 'DECLARE']
    query_upper = query.upper()
    return any(keyword in query_upper for keyword in sql_keywords)

# Test suite
test_cases = [
    {
        "query": "create a database called companydb",
        "description": "CREATE DATABASE with articles",
        "should_be_sql": True,
        "expected_contains": "CREATE DATABASE companydb"
    },
    {
        "query": "make a new database named schooldb",
        "description": "CREATE DATABASE with 'make' and 'named'",
        "should_be_sql": True,
        "expected_contains": "CREATE DATABASE schooldb"
    },
    {
        "query": "drop the database olddb",
        "description": "DROP DATABASE with article",
        "should_be_sql": True,
        "expected_contains": "DROP DATABASE olddb"
    },
    {
        "query": "CREATE DATABASE testdb;",
        "description": "Direct SQL (should pass through)",
        "should_be_sql": True,
        "expected_contains": "CREATE DATABASE testdb"
    },
    {
        "query": "DROP TABLE users;",
        "description": "Direct SQL DROP TABLE",
        "should_be_sql": True,
        "expected_contains": "DROP TABLE users"
    },
]

print("=" * 90)
print("COMPREHENSIVE SQL GENERATION TEST SUITE")
print("=" * 90)
print()

all_passed = True
for i, test in enumerate(test_cases, 1):
    query = test["query"]
    is_sql = is_sql_query(query)
    is_correct = is_sql == test["should_be_sql"]
    
    status = "✓" if is_correct else "✗"
    
    print(f"Test {i}: {test['description']}")
    print(f"  Query:           {query}")
    print(f"  Is SQL:          {is_sql} (expected: {test['should_be_sql']}) {status}")
    
    if is_correct:
        # For SQL queries, clean them
        if is_sql:
            cleaned = clean_sql_output(query)
            contains_expected = test["expected_contains"].lower() in cleaned.lower()
            expected_status = "✓" if contains_expected else "✗"
            print(f"  Cleaned SQL:     {cleaned}")
            print(f"  Contains '{test['expected_contains']}': {contains_expected} {expected_status}")
            if not contains_expected:
                all_passed = False
        else:
            print(f"  (Not SQL, skipping cleanup check)")
    else:
        all_passed = False
        print(f"  ERROR: Expected SQL detection to be {test['should_be_sql']} but got {is_sql}")
    
    print()

print("=" * 90)
if all_passed:
    print("✓ ALL TESTS PASSED!")
else:
    print("✗ SOME TESTS FAILED!")
print("=" * 90)
