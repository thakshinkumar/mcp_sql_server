#!/usr/bin/env python3
"""Focused regression tests for NL-to-SQL sorting phrases."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from mssql_mcp_server.api import main


def run_case(query: str, expected_sql: str):
    actual = main.nl_to_sql_mock(query)
    passed = actual == expected_sql
    status = "PASS" if passed else "FAIL"
    print(f"{status}: {query}")
    print(f"  expected: {expected_sql}")
    print(f"  actual:   {actual}")
    print()
    return passed


def main_test():
    original_get_table_columns = main.get_table_columns

    try:
        # Avoid live DB dependency; enforce the schema from the prompt.
        main.get_table_columns = lambda table_name: [("id", "int", "NO"), ("name", "varchar", "YES"), ("age", "int", "YES")]

        cases = [
            (
                "display users ordered by age from highest to lowest",
                "SELECT * FROM users ORDER BY age DESC;",
            ),
            (
                "show youngest users",
                "SELECT * FROM users ORDER BY age ASC;",
            ),
            (
                "get top 3 oldest users",
                "SELECT TOP 3 * FROM users ORDER BY age DESC;",
            ),
            (
                "display users ordered by age from lowest to highest",
                "SELECT * FROM users ORDER BY age ASC;",
            ),
        ]

        all_passed = True
        for query, expected_sql in cases:
            all_passed = run_case(query, expected_sql) and all_passed

        if not all_passed:
            raise SystemExit(1)

        print("All sorting NL-to-SQL regression tests passed.")
    finally:
        main.get_table_columns = original_get_table_columns


if __name__ == "__main__":
    main_test()
