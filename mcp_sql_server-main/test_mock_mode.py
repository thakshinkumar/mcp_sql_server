#!/usr/bin/env python3
"""Direct test of nl_to_sql_mock function"""

import sys
import re
sys.path.insert(0, 'src')
import re

def clean_sql_output(sql: str) -> str:
    '''"Remove articles (a, an, the) from SQL statements and clean whitespace"""
    # Remove standalone articles (a, an, the) between SQL keywords
    sql = re.sub(r'\\b(CREATE|DROP|ALTER|ADD|MODIFY|TRUNCATE)\\s+(a|an|the)\\s+', r'\\1 ', sql, flags=re.IGNORECASE)
    sql = re.sub(r'\\s+(a|an|the)\\s+(DATABASE|TABLE|COLUMN)\\b', r' \\2', sql, flags=re.IGNORECASE)
    # Clean up extra whitespace
    sql = re.sub(r'\\s+', ' ', sql)
    return sql.strip()

def extract_table_name(query: str) -> str:
    '''Extract table name from natural language query'''
    query_lower = query.lower()
    
    # Pattern 1: "table users" or "from users"
    match = re.search(r'(?:table|from|in)\\s+(\\w+)', query_lower)
    if match:
        return match.group(1)
    
    # Pattern 2: "users table"
    match = re.search(r'(\\w+)\\s+table', query_lower)
    if match:
        return match.group(1)
    
    # Pattern 3: "called users" or "named users"
    match = re.search(r'(?:called|named|as)\\s+(\\w+)', query_lower)
    if match:
        return match.group(1)
    
    return "new_table"

def nl_to_sql_mock_test(nl_query: str) -> str:
    '''Simplified mock SQL generator for testing'''
    query_lower = nl_query.lower()
    
    # Rule 0: CREATE DATABASE
    if ('create' in query_lower or 'make' in query_lower or 'new' in query_lower) and 'database' in query_lower:
        db_match = re.search(r'(?:create|make|new)(?:\\s+a)?\\s+(?:new\\s+)?(?:database|db)\\s+(?:called|named|as)?\\s*(\\w+)', query_lower)
        if db_match:
            db_name = db_match.group(1)
            return f"CREATE DATABASE {db_name};"
    
    # Rule 1: DROP DATABASE
    if ('drop' in query_lower or 'delete' in query_lower or 'remove' in query_lower) and 'database' in query_lower:
        db_match = re.search(r'(?:drop|delete|remove)\\s+(?:the\\s+)?(?:database|db)\\s+(?:called|named)?\\s*(\\w+)', query_lower)
        if db_match:
            db_name = db_match.group(1)
            return f"DROP DATABASE {db_name};"
    
    return "SELECT 1;"

# Test cases
test_queries = [
    "create a database called companydb",
    "make a new database named schooldb",
    "drop the database olddb",
    "create database testdb",
]

print("Testing nl_to_sql_mock with cleanup:")
print("=" * 80)

for query in test_queries:
    sql_before_clean = nl_to_sql_mock_test(query)
    sql_after_clean = clean_sql_output(sql_before_clean)
    print(f"Query:       {query}")
    print(f"Generated:   {sql_before_clean}")
    print(f"Cleaned:     {sql_after_clean}")
    print()
""")
