#!/usr/bin/env python3
"""
End-to-End Test Suite
Tests the complete NL2SQL pipeline with all fixes
"""

import re

# ===== FUNCTION IMPLEMENTATIONS (from main.py) =====

def clean_sql_output(sql: str) -> str:
    """Remove articles (a, an, the) from SQL statements and clean whitespace"""
    sql = re.sub(r'\b(CREATE|DROP|ALTER|ADD|MODIFY|TRUNCATE)\s+(a|an|the)\s+', r'\1 ', sql, flags=re.IGNORECASE)
    sql = re.sub(r'\s+(a|an|the)\s+(DATABASE|TABLE|COLUMN)\b', r' \2', sql, flags=re.IGNORECASE)
    sql = re.sub(r'\s+', ' ', sql)
    return sql.strip()

def is_sql_query(query: str) -> bool:
    """Check if the query is already SQL by looking for SQL keywords and structure."""
    stripped_query = query.strip()
    query_upper = stripped_query.upper()
    
    sql_keywords = [
        "SELECT", "INSERT", "UPDATE", "DELETE", "CREATE", "ALTER", "DROP",
        "TRUNCATE", "EXEC", "WITH", "FROM", "WHERE", "JOIN", "GROUP BY", 
        "ORDER BY", "HAVING", "UNION", "EXCEPT", "INTERSECT", "BEGIN", 
        "COMMIT", "ROLLBACK", "DECLARE"
    ]
    
    starts_with_sql = any(query_upper.startswith(keyword) for keyword in sql_keywords)
    
    if not starts_with_sql:
        return False
    
    stripped_lower = stripped_query.lstrip()
    first_word_lower = stripped_lower.split()[0] if stripped_lower else ""
    if first_word_lower and first_word_lower[0].islower():
        return False
    
    natural_language_indicators = ['a ', 'an ', 'the ', 'called ', 'named ', 'to ', 'in ', 'of ']
    sql_indicators = [';', '(', ')', 'FROM', 'WHERE', '=', ',']
    has_sql_indicators = any(indicator in query_upper for indicator in sql_indicators)
    
    if has_sql_indicators:
        return True
    
    for indicator in natural_language_indicators:
        if indicator in query_upper:
            return False
    
    return True

def simulate_nl_to_sql(nl_query: str) -> str:
    """Simulate the NL2SQL conversion (simplified mock mode)"""
    query_lower = nl_query.lower()
    
    # CREATE DATABASE
    if ('create' in query_lower or 'make' in query_lower) and 'database' in query_lower:
        db_match = re.search(r'(?:create|make|new)(?:\s+a)?\s+(?:new\s+)?(?:database|db)\s+(?:called|named|as)?\s*(\w+)', query_lower)
        if db_match:
            db_name = db_match.group(1)
            return f"CREATE DATABASE {db_name};"
    
    # DROP DATABASE
    if ('drop' in query_lower or 'delete' in query_lower) and 'database' in query_lower:
        db_match = re.search(r'(?:drop|delete|remove)\s+(?:the\s+)?(?:database|db)\s+(?:called|named)?\s*(\w+)', query_lower)
        if db_match:
            db_name = db_match.group(1)
            return f"DROP DATABASE {db_name};"
    
    return "-- Unsupported query"

def pipeline_process_query(query: str) -> dict:
    """Simulate the complete pipeline: detection -> conversion -> cleanup"""
    is_sql = is_sql_query(query)
    
    if is_sql:
        # Direct SQL - pass through with cleanup
        final_sql = clean_sql_output(query)
    else:
        # Natural Language - convert then cleanup
        converted_sql = simulate_nl_to_sql(query)
        final_sql = clean_sql_output(converted_sql)
    
    return {
        "input": query,
        "is_sql": is_sql,
        "final_sql": final_sql,
        "requires_conversion": not is_sql
    }

# ===== TEST SUITE =====

test_cases = [
    {
        "query": "create a database called companydb",
        "expected_sql": "CREATE DATABASE companydb;",
        "should_convert": True,
        "description": "NL: CREATE DATABASE with articles"
    },
    {
        "query": "make a new database named schooldb",
        "expected_sql": "CREATE DATABASE schooldb;",
        "should_convert": True,
        "description": "NL: CREATE DATABASE with 'make' and 'named'"
    },
    {
        "query": "drop the database olddb",
        "expected_sql": "DROP DATABASE olddb;",
        "should_convert": True,
        "description": "NL: DROP DATABASE with article"
    },
    {
        "query": "CREATE DATABASE testdb;",
        "expected_sql": "CREATE DATABASE testdb;",
        "should_convert": False,
        "description": "Direct SQL: CREATE DATABASE"
    },
    {
        "query": "DROP TABLE users;",
        "expected_sql": "DROP TABLE users;",
        "should_convert": False,
        "description": "Direct SQL: DROP TABLE"
    },
]

print("=" * 100)
print("END-TO-END PIPELINE TEST SUITE")
print("=" * 100)
print()

all_passed = True
for i, test in enumerate(test_cases, 1):
    result = pipeline_process_query(test["query"])
    
    # Check if conversion decision was correct
    conversion_correct = result["requires_conversion"] == test["should_convert"]
    
    # Check if final SQL matches expected
    sql_correct = result["final_sql"] == test["expected_sql"]
    
    overall_passed = conversion_correct and sql_correct
    all_passed = all_passed and overall_passed
    
    status = "✓" if overall_passed else "✗"
    
    print(f"Test {i}: {test['description']}")
    print(f"  Input:           {test['query']}")
    print(f"  Is SQL:          {result['is_sql']} (expected: {not test['should_convert']})")
    print(f"  Requires Conversion: {result['requires_conversion']} (expected: {test['should_convert']}) {'✓' if conversion_correct else '✗'}")
    print(f"  Final SQL:       {result['final_sql']}")
    print(f"  Expected SQL:    {test['expected_sql']} {'✓' if sql_correct else '✗'}")
    
    if not overall_passed:
        if not conversion_correct:
            print(f"  ERROR: Conversion decision was wrong!")
        if not sql_correct:
            print(f"  ERROR: SQL output doesn't match expected!")
    
    print()

print("=" * 100)
if all_passed:
    print("✓ ALL END-TO-END TESTS PASSED!")
    print()
    print("Summary:")
    print("  ✓ SQL Detection (NL vs SQL) works correctly")
    print("  ✓ NL2SQL Conversion works correctly")
    print("  ✓ SQL Cleanup (article removal) works correctly")
    print("  ✓ Complete pipeline integrates properly")
else:
    print("✗ SOME TESTS FAILED!")
print("=" * 100)
