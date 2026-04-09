#!/usr/bin/env python
"""Check what's in your SQL Server database."""

import os
import sys
import pymssql
from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, 'src')
from mssql_mcp_server.server import get_db_config

def check_database():
    """Show all tables and their data in the database."""
    print("\n" + "="*60)
    print("  SQL SERVER DATABASE INSPECTOR")
    print("="*60)
    
    config = get_db_config()
    print(f"\nConnected to: {config['server']}:{config.get('port', 1433)}")
    print(f"Database: {config['database']}")
    print("="*60)
    
    conn = pymssql.connect(**config)
    cursor = conn.cursor()
    
    # Get all user tables
    print("\n📊 USER TABLES:")
    print("-"*60)
    cursor.execute("""
        SELECT TABLE_SCHEMA, TABLE_NAME 
        FROM INFORMATION_SCHEMA.TABLES 
        WHERE TABLE_TYPE = 'BASE TABLE' 
        AND TABLE_SCHEMA NOT IN ('sys', 'INFORMATION_SCHEMA')
        ORDER BY TABLE_SCHEMA, TABLE_NAME
    """)
    
    tables = cursor.fetchall()
    
    if not tables:
        print("   No user tables found.")
    else:
        for schema, table in tables:
            full_name = f"{schema}.{table}"
            print(f"\n   📋 {full_name}")
            
            # Get row count
            try:
                cursor.execute(f"SELECT COUNT(*) FROM [{schema}].[{table}]")
                count = cursor.fetchone()[0]
                print(f"      Rows: {count}")
                
                # Show first 3 rows if any
                if count > 0:
                    cursor.execute(f"SELECT TOP 3 * FROM [{schema}].[{table}]")
                    rows = cursor.fetchall()
                    if cursor.description:
                        columns = [desc[0] for desc in cursor.description]
                        print(f"      Columns: {', '.join(columns)}")
                        print(f"      Sample data:")
                        for row in rows:
                            print(f"        {row}")
            except Exception as e:
                print(f"      Error reading table: {e}")
    
    # Get all databases
    print("\n\n🗄️  ALL DATABASES ON SERVER:")
    print("-"*60)
    cursor.execute("SELECT name FROM sys.databases ORDER BY name")
    databases = cursor.fetchall()
    for db in databases:
        current = " (CURRENT)" if db[0] == config['database'] else ""
        print(f"   • {db[0]}{current}")
    
    print("\n" + "="*60)
    print("  INSPECTION COMPLETE")
    print("="*60 + "\n")
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    check_database()
