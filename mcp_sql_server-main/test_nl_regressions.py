#!/usr/bin/env python3
"""Regression tests for broken NL-to-SQL cases from manual testing screenshots."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from mssql_mcp_server.api import main


def check_case(query: str, expected_sql: str) -> bool:
    actual = main.nl_to_sql_mock(query)
    ok = actual == expected_sql
    status = "PASS" if ok else "FAIL"
    print(f"{status}: {query}")
    print(f"  expected: {expected_sql}")
    print(f"  actual:   {actual}")
    print()
    return ok


def main_test():
    original_get_table_columns = main.get_table_columns

    try:
        main.get_table_columns = lambda table_name: [
            ("id", "int", "NO"),
            ("name", "varchar", "YES"),
            ("age", "int", "YES"),
            ("email", "varchar", "YES"),
        ]

        cases = [
            (
                "get users where age is not equal to 25",
                "SELECT * FROM users WHERE age <> 25;",
            ),
            (
                "get the two youngest users",
                "SELECT TOP 2 * FROM users ORDER BY age ASC;",
            ),
            (
                "show users whose name starts with A",
                "SELECT * FROM users WHERE name LIKE 'A%';",
            ),
            (
                "find users whose name ends with i",
                "SELECT * FROM users WHERE name LIKE '%i';",
            ),
            (
                "display users whose name contains the letter r",
                "SELECT * FROM users WHERE name LIKE '%r%';",
            ),
            (
                "count total number of users",
                "SELECT COUNT(*) AS count FROM users;",
            ),
            (
                "find the maximum age of users",
                "SELECT MAX(age) AS max_age FROM users;",
            ),
            (
                "get the minimum age among users",
                "SELECT MIN(age) AS min_age FROM users;",
            ),
            (
                "calculate the average age of users",
                "SELECT AVG(age) AS average_age FROM users;",
            ),
            (
                "remove users older than 28",
                "DELETE FROM users WHERE age > 28;",
            ),
            (
                "delete users whose name starts with K",
                "DELETE FROM users WHERE name LIKE 'K%';",
            ),
            (
                "delete all users where age is less than 23",
                "DELETE FROM users WHERE age < 23;",
            ),
            (
                "show users where age is greater than 22 and less than 30",
                "SELECT * FROM users WHERE age > 22 AND age < 30;",
            ),
            (
                "find users whose name is John or Ravi",
                "SELECT * FROM users WHERE name = 'john' OR name = 'ravi';",
            ),
        ]

        all_ok = True
        for query, expected in cases:
            all_ok = check_case(query, expected) and all_ok

        if not all_ok:
            raise SystemExit(1)

        print("All NL regression tests passed.")
    finally:
        main.get_table_columns = original_get_table_columns


if __name__ == "__main__":
    main_test()
