#!/usr/bin/env python3
"""Test clean_sql_output function"""

# Test the clean_sql_output function inline
import re

def clean_sql_output(sql: str) -> str:
    """Remove articles (a, an, the) from SQL statements and clean whitespace"""
    # Remove standalone articles (a, an, the) between SQL keywords
    sql = re.sub(r'\b(CREATE|DROP|ALTER|ADD|MODIFY|TRUNCATE)\s+(a|an|the)\s+', r'\1 ', sql, flags=re.IGNORECASE)
    sql = re.sub(r'\s+(a|an|the)\s+(DATABASE|TABLE|COLUMN)\b', r' \2', sql, flags=re.IGNORECASE)
    # Clean up extra whitespace
    sql = re.sub(r'\s+', ' ', sql)
    return sql.strip()

# Test cases
test_cases = [
    ('CREATE a DATABASE companydb;', 'CREATE DATABASE companydb;'),
    ('DROP the TABLE oldtable;', 'DROP TABLE oldtable;'),
    ('CREATE  a  DATABASE   test;', 'CREATE DATABASE test;'),
    ('ALTER TABLE users ADD a email VARCHAR(255);', 'ALTER TABLE users ADD email VARCHAR(255);'),
    ('DROP the DATABASE testdb;', 'DROP DATABASE testdb;'),
]

print("Testing clean_sql_output function:")
print("=" * 80)

all_passed = True
for input_sql, expected in test_cases:
    result = clean_sql_output(input_sql)
    passed = result == expected
    all_passed = all_passed and passed
    status = "✓" if passed else "✗"
    print(f"{status} Input:    {input_sql}")
    print(f"  Expected: {expected}")
    print(f"  Got:      {result}")
    if not passed:
        print(f"  MISMATCH!")
    print()

print("=" * 80)
if all_passed:
    print("✓ All tests PASSED!")
else:
    print("✗ Some tests FAILED!")
