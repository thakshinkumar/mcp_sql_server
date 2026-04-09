#!/usr/bin/env python3
"""
Check if employees table exists in the database
"""

import sys
sys.path.insert(0, 'src')

# Import the get_connection function from main
from mssql_mcp_server.api.main import get_connection

try:
    conn = get_connection()
    cursor = conn.cursor()
    
    print("=" * 80)
    print("DATABASE TABLE CHECK")
    print("=" * 80)
    print()
    
    # Check if employees table exists
    print("Checking if 'employees' table exists...")
    cursor.execute("""
        SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES 
        WHERE TABLE_NAME = 'employees' AND TABLE_TYPE = 'BASE TABLE'
    """)
    result = cursor.fetchone()
    
    if result:
        print(f"✗ Table EXISTS: {result[0]}")
        print()
        print("This is likely why CREATE TABLE fails!")
        print()
        print("Listing all tables in database:")
        cursor.execute("""
            SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_TYPE = 'BASE TABLE'
            ORDER BY TABLE_NAME
        """)
        tables = cursor.fetchall()
        for table in tables:
            print(f"  - {table[0]}")
    else:
        print("✓ Table does NOT exist - ready for CREATE TABLE")
        print()
        print("Listing all tables in database:")
        cursor.execute("""
            SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_TYPE = 'BASE TABLE'
            ORDER BY TABLE_NAME
        """)
        tables = cursor.fetchall()
        if tables:
            for table in tables:
                print(f"  - {table[0]}")
        else:
            print("  (No tables found)")
    
    print()
    print("=" * 80)
    
    conn.close()
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
