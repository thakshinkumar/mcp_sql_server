#!/usr/bin/env python
"""Helper to execute SQL queries from command line."""

import os
import sys
import asyncio

# Set environment variables
os.environ["MSSQL_SERVER"] = "localhost"
os.environ["MSSQL_PORT"] = "50998"
os.environ["MSSQL_DATABASE"] = "master"
os.environ["MSSQL_WINDOWS_AUTH"] = "true"

sys.path.insert(0, 'src')

from mssql_mcp_server.server import call_tool

async def run_query(query):
    result = await call_tool('execute_sql', {'query': query})
    for content in result:
        print(content.text)

if __name__ == "__main__":
    query = sys.argv[1] if len(sys.argv) > 1 else "SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'"
    asyncio.run(run_query(query))
