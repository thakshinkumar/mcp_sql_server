#!/usr/bin/env python
"""Interactive SQL query tester using MCP server."""

import os
import sys
import asyncio

# Set environment variables
os.environ["MSSQL_SERVER"] = "localhost"
os.environ["MSSQL_PORT"] = "50998"
os.environ["MSSQL_DATABASE"] = "master"
os.environ["MSSQL_WINDOWS_AUTH"] = "true"

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from mssql_mcp_server.server import list_resources, call_tool

async def run_query(query):
    """Execute a SQL query and display results."""
    try:
        result = await call_tool("execute_sql", {"query": query})
        print("\n" + "="*60)
        print("RESULTS:")
        print("="*60)
        for content in result:
            print(content.text)
        print("="*60 + "\n")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}\n")

async def list_tables():
    """List all tables in the database."""
    try:
        resources = await list_resources()
        print("\n" + "="*60)
        print("TABLES IN DATABASE:")
        print("="*60)
        for resource in resources:
            print(f"  • {resource.name}")
        print("="*60 + "\n")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}\n")

async def main():
    """Main interactive loop."""
    print("\n" + "="*60)
    print("  SQL SERVER INTERACTIVE TESTER")
    print("="*60)
    print("\nConnected to: localhost:50998/master")
    print("\nCommands:")
    print("  1. Type 'tables' - List all tables")
    print("  2. Type any SQL query - Execute it")
    print("  3. Type 'exit' or 'quit' - Exit")
    print("\nExamples:")
    print("  • SELECT @@VERSION")
    print("  • SELECT * FROM spt_monitor")
    print("  • CREATE TABLE test (id INT, name VARCHAR(50))")
    print("="*60 + "\n")
    
    while True:
        try:
            user_input = input("SQL> ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['exit', 'quit', 'q']:
                print("\n👋 Goodbye!\n")
                break
            
            if user_input.lower() == 'tables':
                await list_tables()
            else:
                await run_query(user_input)
                
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!\n")
            break
        except EOFError:
            print("\n\n👋 Goodbye!\n")
            break

if __name__ == "__main__":
    asyncio.run(main())
