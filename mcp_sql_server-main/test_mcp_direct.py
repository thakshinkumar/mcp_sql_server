#!/usr/bin/env python
"""Direct test of MCP server functionality."""

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

from mssql_mcp_server.server import app

async def test_mcp():
    """Test MCP server tools."""
    print("Testing MCP Server Tools...\n")
    
    # Import the actual handler functions
    from mssql_mcp_server.server import list_tools, list_resources, call_tool
    
    # Test 1: List tools
    print("1. Listing available tools:")
    tools = await list_tools()
    for tool in tools:
        print(f"   - {tool.name}: {tool.description}")
    
    # Test 2: List resources (tables)
    print("\n2. Listing database tables:")
    resources = await list_resources()
    for resource in resources:
        print(f"   - {resource.name}")
    
    # Test 3: Execute a simple query
    print("\n3. Testing SQL query execution:")
    result = await call_tool("execute_sql", {"query": "SELECT @@VERSION"})
    print(f"   SQL Server Version:")
    for content in result:
        print(f"   {content.text[:100]}...")
    
    print("\n✅ All tests passed!")

if __name__ == "__main__":
    asyncio.run(test_mcp())
