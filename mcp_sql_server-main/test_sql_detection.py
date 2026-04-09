#!/usr/bin/env python3
"""Test the improved is_sql_query function"""

def is_sql_query(query: str) -> bool:
    """Check if the query is already SQL by looking for SQL keywords and structure."""
    stripped_query = query.strip()
    query_upper = stripped_query.upper()
    
    # SQL keywords that typically start a statement
    sql_keywords = [
        "SELECT", "INSERT", "UPDATE", "DELETE", "CREATE", "ALTER", "DROP",
        "TRUNCATE", "EXEC", "WITH", "FROM", "WHERE", "JOIN", "GROUP BY", 
        "ORDER BY", "HAVING", "UNION", "EXCEPT", "INTERSECT", "BEGIN", 
        "COMMIT", "ROLLBACK", "DECLARE"
    ]
    
    # Check if it starts with a SQL keyword
    starts_with_sql = any(query_upper.startswith(keyword) for keyword in sql_keywords)
    
    if not starts_with_sql:
        return False
    
    # If starts with SQL keyword, apply additional heuristics to distinguish SQL from NL
    # 1. If starts with LOWERCASE SQL keyword, it's probably natural language
    stripped_lower = stripped_query.lstrip()
    first_word_lower = stripped_lower.split()[0] if stripped_lower else ""
    if first_word_lower and first_word_lower[0].islower():
        # Starts with lowercase keyword - probably natural language
        return False
    
    # 2. Check for natural language patterns mixed with keywords
    natural_language_indicators = ['a ', 'an ', 'the ', 'called ', 'named ', 'to ', 'in ', 'of ']
    
    # If it has SQL structure indicators, it's probably real SQL
    sql_indicators = [';', '(', ')', 'FROM', 'WHERE', '=', ',']
    has_sql_indicators = any(indicator in query_upper for indicator in sql_indicators)
    
    if has_sql_indicators:
        # More likely to be actual SQL
        return True
    
    # If it has natural language patterns, it's probably NL
    for indicator in natural_language_indicators:
        if indicator in query_upper:
            # Has natural language patterns - probably NL
            return False
    
    # Default: if starts with uppercase SQL keyword and has structure, treat as SQL
    return True

# Test cases
test_cases = [
    # Natural Language (should return False)
    ("create a database called companydb", False, "NL: create a database"),
    ("make a new database named schooldb", False, "NL: make a database"),
    ("drop the database olddb", False, "NL: drop the database"),
    ("create a table with id and name", False, "NL: create a table with columns"),
    ("show all tables", False, "NL: show all tables"),
    ("describe the users table", False, "NL: describe table"),
    
    # Actual SQL (should return True)
    ("CREATE DATABASE testdb;", True, "SQL: CREATE DATABASE"),
    ("DROP TABLE users;", True, "SQL: DROP TABLE"),
    ("SELECT * FROM users;", True, "SQL: SELECT statement"),
    ("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS", True, "SQL: SELECT from schema"),
    ("CREATE TABLE users (id INT, name VARCHAR(100));", True, "SQL: CREATE TABLE with schema"),
    ("ALTER TABLE users ADD email VARCHAR(255);", True, "SQL: ALTER TABLE"),
    ("TRUNCATE TABLE orders;", True, "SQL: TRUNCATE"),
]

print("=" * 100)
print("IMPROVED is_sql_query() DETECTION TEST")
print("=" * 100)
print()

all_passed = True
for query, expected, description in test_cases:
    result = is_sql_query(query)
    passed = result == expected
    all_passed = all_passed and passed
    
    status = "✓" if passed else "✗"
    result_text = "SQL" if result else "NL"
    expected_text = "SQL" if expected else "NL"
    
    print(f"{status} {description}")
    print(f"  Query:    {query}")
    print(f"  Detected: {result_text}, Expected: {expected_text}")
    if not passed:
        print(f"  ERROR: Expected {expected_text} but got {result_text}!")
    print()

print("=" * 100)
if all_passed:
    print("✓ ALL TESTS PASSED!")
else:
    print("✗ SOME TESTS FAILED!")
print("=" * 100)
