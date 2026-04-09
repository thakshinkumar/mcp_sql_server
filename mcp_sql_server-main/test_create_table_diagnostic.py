#!/usr/bin/env python3
"""
Diagnostic test for CREATE TABLE issue
This helps identify what's going wrong with CREATE TABLE execution
"""

# Test 1: Check if table already exists
import pyodbc
import sys

try:
    # Connection parameters (adjust as needed)
    conn = pyodbc.connect(
        driver='{ODBC Driver 17 for SQL Server}',
        server='localhost\\SQLEXPRESS',
        database='testdb',
        trusted_connection='yes'
    )
    cursor = conn.cursor()
    
    print("=" * 80)
    print("DIAGNOSTIC TEST FOR CREATE TABLE ISSUE")
    print("=" * 80)
    print()
    
    # Test 1: Check if employees table exists
    print("Test 1: Checking if employees table exists...")
    cursor.execute("""
        SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES 
        WHERE TABLE_NAME = 'employees' AND TABLE_TYPE = 'BASE TABLE'
    """)
    result = cursor.fetchone()
    if result:
        print("  ✓ employees table EXISTS - This might be why CREATE TABLE fails!")
        
        # Try to drop it
        print("  Attempt to drop existing table...")
        try:
            cursor.execute("DROP TABLE employees;")
            conn.commit()
            print("  ✓ Successfully dropped employees table")
        except Exception as e:
            print(f"  ✗ Failed to drop: {e}")
    else:
        print("  ✓ employees table does NOT exist")
    print()
    
    # Test 2: Try CREATE TABLE with IF NOT EXISTS
    print("Test 2: Testing CREATE TABLE IF NOT EXISTS...")
    test_sql = "CREATE TABLE employees (id INT PRIMARY KEY, name VARCHAR(100), salary DECIMAL(10,2));"
    try:
        print(f"  Executing: {test_sql}")
        cursor.execute(test_sql)
        conn.commit()
        print("  ✓ CREATE TABLE succeeded!")
    except Exception as e:
        print(f"  ✗ CREATE TABLE failed: {e}")
        print(f"  Error type: {type(e).__name__}")
        conn.rollback()
    print()
    
    # Test 3: Check table structure if it exists now
    print("Test 3: Checking table structure...")
    try:
        cursor.execute("""
            SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = 'employees'
            ORDER BY ORDINAL_POSITION
        """)
        rows = cursor.fetchall()
        if rows:
            print("  Table columns:")
            for row in rows:
                print(f"    - {row[0]}: {row[1]} (nullable: {row[2]})")
        else:
            print("  ✗ No columns found (table may not exist)")
    except Exception as e:
        print(f"  Error: {e}")
    print()
    
    # Test 4: Check connection autocommit setting
    print("Test 4: Connection settings...")
    print(f"  Autocommit: {conn.autocommit}")
    print(f"  Driver: {conn.driver}")
    print()
    
    conn.close()
    print("=" * 80)
    print("DIAGNOSTIC TEST COMPLETE")
    print("=" * 80)
    
except Exception as e:
    print(f"Connection error: {e}")
    sys.exit(1)
