#!/usr/bin/env python
"""Test script for POC demonstration."""

import os
import sys
import asyncio

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

import pymssql
from mssql_mcp_server.orchestrator import orchestrator
from mssql_mcp_server.server import get_db_config


async def test_poc():
    """Test the complete POC system."""
    print("\n" + "="*60)
    print("  VOICE-ENABLED SELF-OPTIMIZING SQL SERVER - POC TEST")
    print("="*60 + "\n")
    
    # Connect to database
    print("1. Connecting to database...")
    db_config = get_db_config()
    conn = pymssql.connect(**db_config)
    print("   ✓ Connected successfully\n")
    
    # Test queries
    test_queries = [
        "List all tables in my database",
        "Show me the SQL Server version",
        "List all tables in my database",  # Test cache
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. Testing Query: '{query}'")
        print("-" * 60)
        
        result = orchestrator.process_query(query, conn)
        
        print(f"   Input: {result['input']}")
        print(f"   Cached: {result['cached']}")
        print(f"   Candidates Generated: {len(result['candidates'])}")
        
        if result['candidates']:
            print(f"   Selected SQL: {result['selected_sql'][:100]}...")
        
        if result['metrics']:
            print(f"   Execution Time: {result['metrics'].get('execution_time_ms', 0):.2f} ms")
            print(f"   Success: {result['metrics'].get('success', False)}")
        
        if result['error']:
            print(f"   ❌ Error: {result['error']}")
        else:
            print(f"   ✓ Success")
        
        print("-" * 60)
    
    # Show statistics
    print("\n" + "="*60)
    print("  SYSTEM STATISTICS")
    print("="*60)
    
    stats = orchestrator.get_stats()
    
    print("\nCache Stats:")
    cache_stats = stats['cache']
    print(f"   Hits: {cache_stats['hits']}")
    print(f"   Misses: {cache_stats['misses']}")
    print(f"   Hit Rate: {cache_stats['hit_rate']:.2%}")
    print(f"   Size: {cache_stats['size']}/{cache_stats['max_size']}")
    
    print("\nRL Agent Stats:")
    rl_stats = stats['rl_agent']
    print(f"   Enabled: {rl_stats['enabled']}")
    print(f"   Total Updates: {rl_stats['total_updates']}")
    print(f"   Explorations: {rl_stats['explorations']}")
    print(f"   Exploitations: {rl_stats['exploitations']}")
    print(f"   Epsilon: {rl_stats['epsilon']:.3f}")
    print(f"   Q-Table Size: {rl_stats['q_table_size']}")
    
    print("\n" + "="*60)
    print("  POC TEST COMPLETED")
    print("="*60 + "\n")
    
    conn.close()


if __name__ == "__main__":
    asyncio.run(test_poc())
